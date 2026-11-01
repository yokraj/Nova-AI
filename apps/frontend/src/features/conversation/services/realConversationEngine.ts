import { APP_CONFIG } from '@/config/app.config';
import { ResponseBlock } from '../types/message';

export interface StreamUpdatePayload {
  thinkingStage?: string;
  streamingContent?: string;
  isComplete?: boolean;
  blocks?: ResponseBlock[];
}

function parseBlocksFromText(rawText: string): ResponseBlock[] {
  let displayContent = rawText;
  
  // Format or strip thinking tags cleanly
  if (displayContent.includes('<think>') && displayContent.includes('</think>')) {
    const thinkStart = displayContent.indexOf('<think>');
    const thinkEnd = displayContent.indexOf('</think>') + 8;
    const thinkingText = displayContent.substring(thinkStart + 7, thinkEnd - 8).trim();
    const answerText = displayContent.substring(thinkEnd).trim();
    displayContent = answerText || thinkingText;
  } else if (displayContent.startsWith('<think>')) {
    displayContent = displayContent.replace('<think>', 'Thinking:\n').trim();
  }

  // Parse code blocks if present
  const codeBlockRegex = /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g;
  const blocks: ResponseBlock[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = codeBlockRegex.exec(displayContent)) !== null) {
    const textBefore = displayContent.substring(lastIndex, match.index).trim();
    if (textBefore) {
      blocks.push({
        id: `b-txt-${Date.now()}-${blocks.length}`,
        type: 'markdown',
        content: textBefore,
      });
    }

    const language = match[1] || 'plaintext';
    const code = match[2].trim();
    blocks.push({
      id: `b-code-${Date.now()}-${blocks.length}`,
      type: 'code',
      codeData: {
        language,
        code,
        filename: `solution.${language === 'python' ? 'py' : language === 'javascript' || language === 'typescript' ? 'ts' : 'txt'}`,
      },
    });

    lastIndex = match.index + match[0].length;
  }

  const remainingText = displayContent.substring(lastIndex).trim();
  if (remainingText || blocks.length === 0) {
    blocks.push({
      id: `b-txt-${Date.now()}-${blocks.length}`,
      type: 'markdown',
      content: remainingText || displayContent,
    });
  }

  return blocks;
}

export async function executeRealStreamingResponse(
  prompt: string,
  onUpdate: (payload: StreamUpdatePayload) => void,
  abortSignal?: AbortSignal,
  history?: Array<{ role: string; content: string }>,
  conversationId?: string
): Promise<void> {
  // Stage 1: Understanding & Reasoning
  onUpdate({
    thinkingStage: 'UNDERSTANDING',
    streamingContent: 'Analyzing prompt intent...',
  });

  const token = typeof localStorage !== 'undefined' ? localStorage.getItem('nova_auth_token') : null;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'text/event-stream, application/json',
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  let accumulatedText = '';

  // 1. Primary Strategy: Backend SSE Stream
  try {
    const streamUrl = `${APP_CONFIG.apiBaseUrl}/inference/stream`;
    const response = await fetch(streamUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        prompt,
        model: 'qwen3:8b',
        stream: true,
        messages: history && history.length > 0 ? history : undefined,
        conversation_id: conversationId,
      }),
      signal: abortSignal,
    });

    if (response.ok && response.body) {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      onUpdate({ thinkingStage: 'REASONING' });

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data:')) {
            const dataText = line.startsWith('data: ') ? line.substring(6) : line.substring(5);
            if (dataText) {
              accumulatedText += dataText;
              const isStillThinking = accumulatedText.includes('<think>') && !accumulatedText.includes('</think>');
              onUpdate({
                thinkingStage: isStillThinking ? 'REASONING' : 'EXECUTING',
                streamingContent: accumulatedText,
                blocks: parseBlocksFromText(accumulatedText),
              });
            }
          }
        }
      }

      if (accumulatedText.trim()) {
        onUpdate({
          isComplete: true,
          thinkingStage: undefined,
          streamingContent: accumulatedText,
          blocks: parseBlocksFromText(accumulatedText),
        });
        return;
      }
    }
  } catch (streamErr: any) {
    if (abortSignal?.aborted) return;
    console.warn('Backend SSE stream encountered error, attempting direct inference fallback:', streamErr);
  }

  // 2. Secondary Strategy: Backend Non-Streaming POST
  try {
    const chatUrl = `${APP_CONFIG.apiBaseUrl}/inference/chat`;
    const res = await fetch(chatUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        prompt,
        model: 'qwen3:8b',
        messages: history && history.length > 0 ? history : undefined,
        conversation_id: conversationId,
      }),
      signal: abortSignal,
    });

    if (res.ok) {
      const data = await res.json();
      const content = data.content || '';
      if (content) {
        onUpdate({
          isComplete: true,
          thinkingStage: undefined,
          streamingContent: content,
          blocks: parseBlocksFromText(content),
        });
        return;
      }
    }
  } catch (chatErr) {
    console.warn('Backend chat inference unavailable, attempting local Ollama direct fallback:', chatErr);
  }

  // 3. Resilient Local Fallback: Direct Ollama Execution
  try {
    const ollamaUrl = `${APP_CONFIG.ollamaBaseUrl}/api/generate`;
    const res = await fetch(ollamaUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model: 'qwen3:8b',
        prompt,
        stream: false,
      }),
      signal: abortSignal,
    });

    if (res.ok) {
      const data = await res.json();
      const content = data.response || data.thinking || '';
      if (content) {
        onUpdate({
          isComplete: true,
          thinkingStage: undefined,
          streamingContent: content,
          blocks: parseBlocksFromText(content),
        });
        return;
      }
    }
  } catch (ollamaErr) {
    console.error('All inference strategies failed:', ollamaErr);
  }

  // 4. If all fail, display transparent error (Never fake or return mock generic response)
  onUpdate({
    isComplete: true,
    thinkingStage: undefined,
    streamingContent: 'Unable to reach local AI inference engine (Ollama on http://127.0.0.1:11434). Please ensure Ollama is running and qwen3:8b is loaded.',
    blocks: [
      {
        id: `b-err-${Date.now()}`,
        type: 'markdown',
        content:
          '**Error**: Unable to reach local AI inference engine (Ollama on `http://127.0.0.1:11434`).\n\nPlease ensure Ollama service is active and `qwen3:8b` is loaded.',
      },
    ],
  });
}
