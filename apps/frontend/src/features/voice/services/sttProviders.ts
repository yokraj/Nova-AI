import { APP_CONFIG } from '@/config/app.config';

export interface STTTranscriptionResult {
  transcript: string;
  confidence: number;
  language?: string;
  provider: 'local_whisper' | 'browser_webspeech';
}

export interface STTProvider {
  id: string;
  name: string;
  isAvailable(): Promise<boolean> | boolean;
  transcribe(audioBlob: Blob, language?: string): Promise<STTTranscriptionResult>;
}

/**
 * Local-First Offline Speech-To-Text Provider.
 * Sends recorded microphone audio bytes to Nova's local faster-whisper endpoint.
 * Zero-cloud, 100% offline and local execution.
 */
export class LocalWhisperSTTProvider implements STTProvider {
  id = 'local_whisper';
  name = 'Local Whisper Engine';

  async isAvailable(): Promise<boolean> {
    try {
      const res = await fetch(`${APP_CONFIG.apiBaseUrl}/voice/status`, {
        method: 'GET',
        signal: AbortSignal.timeout(2000),
      });
      if (res.ok) {
        const data = await res.json();
        return data.status === 'ready' || data.engine === 'faster-whisper';
      }
      return false;
    } catch {
      return false;
    }
  }

  async transcribe(audioBlob: Blob, language?: string): Promise<STTTranscriptionResult> {
    const formData = new FormData();
    const filename = audioBlob.type.includes('ogg')
      ? 'audio.ogg'
      : audioBlob.type.includes('wav')
      ? 'audio.wav'
      : 'audio.webm';
    formData.append('file', audioBlob, filename);

    const token = typeof localStorage !== 'undefined' ? localStorage.getItem('nova_auth_token') : null;
    const headers: Record<string, string> = {};
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const langQuery = language && language !== 'auto' ? `?language=${encodeURIComponent(language)}` : '';
    const res = await fetch(`${APP_CONFIG.apiBaseUrl}/voice/transcribe${langQuery}`, {
      method: 'POST',
      headers,
      body: formData,
      signal: AbortSignal.timeout(20000),
    });

    if (!res.ok) {
      const errText = await res.text();
      let errorMsg = `Server returned ${res.status}`;
      try {
        const json = JSON.parse(errText);
        errorMsg = json.detail || json.message || errorMsg;
      } catch {
        // fallback
      }
      throw new Error(`Local Whisper transcription error: ${errorMsg}`);
    }

    const data = await res.json();
    return {
      transcript: (data.transcript || '').trim(),
      confidence: data.confidence !== undefined ? data.confidence : 0.95,
      language: data.language || 'en',
      provider: 'local_whisper',
    };
  }
}

/**
 * Browser Web Speech Recognition Provider (Optional Fallback).
 * Used only if local Whisper backend service is temporarily offline or unavailable.
 */
export class BrowserWebSpeechSTTProvider implements STTProvider {
  id = 'browser_webspeech';
  name = 'Browser Web Speech API';

  isAvailable(): boolean {
    return (
      typeof window !== 'undefined' &&
      Boolean((window as any).SpeechRecognition || (window as any).webkitSpeechRecognition)
    );
  }

  async transcribe(_audioBlob: Blob): Promise<STTTranscriptionResult> {
    // MediaRecorder audio blob cannot be fed directly into browser SpeechRecognition
    // because SpeechRecognition only captures live microphone streams.
    throw new Error('Browser SpeechRecognition requires live stream capture.');
  }
}

/**
 * Composite Speech-To-Text Coordinator.
 * Enforces Local Whisper as the primary offline provider, with clear status and error diagnostics.
 */
export class CompositeSTTService {
  private localWhisper = new LocalWhisperSTTProvider();

  async transcribeAudioBlob(audioBlob: Blob, language?: string): Promise<STTTranscriptionResult> {
    // Primary: Local-First Multilingual Whisper
    try {
      return await this.localWhisper.transcribe(audioBlob, language);
    } catch (err: any) {
      console.warn('Local Whisper transcription failure:', err);
      throw err;
    }
  }

  async isLocalWhisperReady(): Promise<boolean> {
    return await this.localWhisper.isAvailable();
  }
}

