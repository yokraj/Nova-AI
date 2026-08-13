import { ModelProvider } from './modelProvider';
import { ModelRequest } from '../types/modelRequest';
import { ModelResponse } from '../types/modelResponse';
import { ExecutionPlan } from '../types/executionPlan';
import { ExecutionStep } from '../types/executionStep';
import { ModelConfigStore } from '../config/modelConfigStore';
import { PromptBuilder } from '../planner/promptBuilder';

export class LocalModelProvider implements ModelProvider {
  providerName = 'LOCAL_MODEL_PROVIDER';
  private promptBuilder = new PromptBuilder();

  async isAvailable(): Promise<boolean> {
    const config = ModelConfigStore.getConfig();
    if (!config.enableLocalModel) return false;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);

    try {
      // First try standard OpenAI /v1/models endpoint
      const res = await fetch(`${config.baseUrl}/models`, {
        method: 'GET',
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return res.ok;
    } catch {
      clearTimeout(timeoutId);
      // Fall back check for Ollama native endpoint /api/tags if /v1/models failed
      try {
        const nativeUrl = config.baseUrl.replace(/\/v1\/?$/, '');
        const controller2 = new AbortController();
        const timeoutId2 = setTimeout(() => controller2.abort(), 3000);
        const res2 = await fetch(`${nativeUrl}/api/tags`, {
          method: 'GET',
          signal: controller2.signal,
        });
        clearTimeout(timeoutId2);
        return res2.ok;
      } catch {
        return false;
      }
    }
  }

  async generatePlan(goal: string, observations?: string[]): Promise<ExecutionPlan> {
    const config = ModelConfigStore.getConfig();
    const isOnline = await this.isAvailable();

    if (!isOnline) {
      throw new Error(`Local model endpoint (${config.baseUrl}) is currently unavailable.`);
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), config.timeoutMs);

    try {
      const systemPrompt = this.promptBuilder.buildSystemPrompt();
      const userPrompt = this.promptBuilder.buildUserPrompt(goal, observations);

      const payload = {
        model: config.model,
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt },
        ],
        temperature: config.temperature,
        max_tokens: config.maxTokens,
        response_format: { type: 'json_object' },
      };

      const response = await fetch(`${config.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`Local LLM HTTP Error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      const rawText = data?.choices?.[0]?.message?.content || '';

      return this.parseStructuredPlan(rawText, goal);
    } catch (err: any) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        throw new Error(`Local LLM execution timed out after ${config.timeoutMs}ms.`);
      }
      throw new Error(`Local LLM planning failed: ${err?.message || 'Unknown model error'}`);
    }
  }

  async generateResponse(request: ModelRequest): Promise<ModelResponse> {
    const isOnline = await this.isAvailable();
    if (!isOnline) {
      return {
        text: 'Local LLM server is currently unavailable.',
        isComplete: false,
      };
    }

    return {
      text: 'Local model processed inference request.',
      isComplete: true,
    };
  }

  private parseStructuredPlan(rawJsonText: string, goal: string): ExecutionPlan {
    let parsed: any;
    try {
      const jsonStart = rawJsonText.indexOf('{');
      const jsonEnd = rawJsonText.lastIndexOf('}');
      const cleanJson = jsonStart !== -1 && jsonEnd !== -1 ? rawJsonText.substring(jsonStart, jsonEnd + 1) : rawJsonText;
      parsed = JSON.parse(cleanJson);
    } catch {
      throw new Error('Local LLM output failed JSON parsing.');
    }

    if (!parsed || !Array.isArray(parsed.steps)) {
      throw new Error('Local LLM response structure missing "steps" array.');
    }

    const steps: ExecutionStep[] = parsed.steps.map((s: any, idx: number) => ({
      id: s.id || `step-${idx + 1}`,
      stepNumber: idx + 1,
      title: s.reason || s.tool || `Step ${idx + 1}`,
      description: s.reason || `Tool execution: ${s.tool}`,
      status: 'PENDING',
      toolCall: s.tool
        ? {
            callId: `call-${idx + 1}-${Date.now()}`,
            toolName: s.tool,
            arguments: s.arguments || {},
          }
        : undefined,
    }));

    return {
      planId: `plan-local-${Date.now()}`,
      goal: parsed.goal || goal,
      steps,
      estimatedDurationSeconds: steps.length * 0.5 + 0.5,
      createdAt: new Date().toISOString(),
    };
  }
}
