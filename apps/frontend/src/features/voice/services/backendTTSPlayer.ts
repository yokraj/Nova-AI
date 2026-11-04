/**
 * Backend Neural Text-To-Speech (TTS) Audio Player Service for Nova OS.
 *
 * Connects directly to Nova's /api/v1/voice/tts/generate backend endpoint
 * to stream and play authentic multilingual Indian speech:
 * - NOVA Indian Professional (en-IN): en-IN-PrabhatNeural
 * - NOVA Tamil Conversational (ta-IN): ta-IN-ValluvarNeural
 * - NOVA Hindi Conversational (hi-IN): hi-IN-MadhurNeural
 *
 * Supports instant barge-in cancellation, volume modulation, and playback lifecycle hooks.
 */

import { APP_CONFIG } from '@/config/app.config';

export interface TTSPlaybackOptions {
  language?: string;
  voice?: string;
  mode?: 'offline' | 'neural';
  pitch?: number;
  speakingRate?: number;
  volume?: number;
  offlineOnly?: boolean;
}

export interface TTSMetadataResult {
  voice: string;
  engine: string;
  mode: 'offline' | 'online';
}

export class BackendTTSAudioPlayer {
  private currentAudio: HTMLAudioElement | null = null;
  private currentObjectUrl: string | null = null;
  private abortController: AbortController | null = null;
  private isPlayingAudio = false;

  public isSupported(): boolean {
    return typeof window !== 'undefined' && typeof Audio !== 'undefined';
  }

  public isSpeaking(): boolean {
    return this.isPlayingAudio;
  }

  /**
   * Immediately halts active audio playback and clears resources for barge-in.
   */
  public stop(): void {
    if (this.abortController) {
      try {
        this.abortController.abort();
      } catch {}
      this.abortController = null;
    }

    if (this.currentAudio) {
      try {
        this.currentAudio.pause();
        this.currentAudio.currentTime = 0;
        this.currentAudio.removeAttribute('src');
        this.currentAudio.load();
      } catch {}
      this.currentAudio = null;
    }

    if (this.currentObjectUrl) {
      try {
        URL.revokeObjectURL(this.currentObjectUrl);
      } catch {}
      this.currentObjectUrl = null;
    }

    this.isPlayingAudio = false;
  }

  /**
   * Synthesizes text via Nova backend and plays genuine audible audio.
   */
  public async synthesizeAndPlay(
    text: string,
    options: TTSPlaybackOptions = {},
    onStart?: () => void,
    onEnd?: () => void,
    onError?: (err: Error) => void
  ): Promise<void> {
    const cleanText = text.trim();
    if (!cleanText) {
      onEnd?.();
      return;
    }

    // Stop any currently playing audio immediately
    this.stop();

    this.abortController = new AbortController();

    try {
      const payload = {
        text: cleanText,
        language: options.language || 'en-IN',
        voice: options.voice || null,
        mode: options.mode || (options.offlineOnly ? 'offline' : 'neural'),
        pitch: options.pitch ?? 1.08,
        rate: options.speakingRate ?? 1.05,
        volume: options.volume ?? 100,
        offline_only: Boolean(options.offlineOnly),
      };

      const token =
        typeof localStorage !== 'undefined' ? localStorage.getItem('nova_auth_token') : null;
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }

      const response = await fetch(`${APP_CONFIG.apiBaseUrl}/voice/tts/generate`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        let errMsg = `HTTP ${response.status}`;
        try {
          const parsed = JSON.parse(errorText);
          errMsg = parsed.detail || parsed.message || errMsg;
        } catch {}
        throw new Error(`TTS synthesis endpoint failed: ${errMsg}`);
      }

      const audioBlob = await response.blob();
      if (!audioBlob || audioBlob.size < 64) {
        throw new Error('TTS server returned empty audio stream.');
      }

      const objectUrl = URL.createObjectURL(audioBlob);
      this.currentObjectUrl = objectUrl;

      const audio = new Audio(objectUrl);
      this.currentAudio = audio;

      const volumeFactor = Math.max(0, Math.min(1, (options.volume ?? 100) / 100));
      audio.volume = volumeFactor;

      audio.onplay = () => {
        this.isPlayingAudio = true;
        onStart?.();
      };

      audio.onended = () => {
        this.cleanup();
        onEnd?.();
      };

      audio.onerror = () => {
        const err = new Error('Audio element failed during playback.');
        this.cleanup();
        onError?.(err);
      };

      await audio.play();
    } catch (err: any) {
      if (err.name === 'AbortError') {
        // Ignored as user interrupted intentionally
        return;
      }
      this.cleanup();
      onError?.(err instanceof Error ? err : new Error(String(err)));
    }
  }

  /**
   * Generates and plays audio preview for the specified voice, returning actual server metadata.
   */
  public async previewVoice(
    sampleText: string,
    options: TTSPlaybackOptions = {},
    onStart?: (meta: TTSMetadataResult) => void,
    onEnd?: () => void,
    onError?: (err: Error) => void
  ): Promise<TTSMetadataResult> {
    const cleanText = sampleText.trim();
    this.stop();
    this.abortController = new AbortController();

    try {
      const payload = {
        text: cleanText,
        language: options.language || 'en-IN',
        voice: options.voice || null,
        mode: options.mode || (options.offlineOnly ? 'offline' : 'neural'),
        pitch: options.pitch ?? 1.08,
        rate: options.speakingRate ?? 1.05,
        volume: options.volume ?? 100,
        offline_only: Boolean(options.offlineOnly),
      };

      const token =
        typeof localStorage !== 'undefined' ? localStorage.getItem('nova_auth_token') : null;
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };
      if (token) headers['Authorization'] = `Bearer ${token}`;

      const response = await fetch(`${APP_CONFIG.apiBaseUrl}/voice/tts/preview`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
        signal: this.abortController.signal,
      });

      if (!response.ok) {
        const errorText = await response.text();
        let errMsg = `HTTP ${response.status}`;
        try {
          const parsed = JSON.parse(errorText);
          errMsg = parsed.detail || parsed.message || errMsg;
        } catch {}
        throw new Error(`Voice preview failed: ${errMsg}`);
      }

      const voiceHeader = response.headers.get('X-Voice-Profile') || options.voice || 'windows-sapi';
      const engineHeader = response.headers.get('X-TTS-Engine') || (options.offlineOnly ? 'windows-sapi' : 'edge-tts');
      const modeHeader = (response.headers.get('X-TTS-Mode') || (options.offlineOnly ? 'offline' : 'online')) as 'offline' | 'online';

      const metadata: TTSMetadataResult = {
        voice: voiceHeader,
        engine: engineHeader,
        mode: modeHeader,
      };

      const audioBlob = await response.blob();
      if (!audioBlob || audioBlob.size < 64) {
        throw new Error('TTS server returned empty audio stream for preview.');
      }

      const objectUrl = URL.createObjectURL(audioBlob);
      this.currentObjectUrl = objectUrl;

      const audio = new Audio(objectUrl);
      this.currentAudio = audio;
      const volumeFactor = Math.max(0, Math.min(1, (options.volume ?? 100) / 100));
      audio.volume = volumeFactor;

      audio.onplay = () => {
        this.isPlayingAudio = true;
        onStart?.(metadata);
      };

      audio.onended = () => {
        this.cleanup();
        onEnd?.();
      };

      audio.onerror = () => {
        const err = new Error('Audio element failed during preview playback.');
        this.cleanup();
        onError?.(err);
      };

      await audio.play();
      return metadata;
    } catch (err: any) {
      if (err.name === 'AbortError') {
        return { voice: options.voice || '', engine: '', mode: 'offline' };
      }
      this.cleanup();
      onError?.(err instanceof Error ? err : new Error(String(err)));
      throw err;
    }
  }

  private cleanup(): void {
    if (this.currentObjectUrl) {
      try {
        URL.revokeObjectURL(this.currentObjectUrl);
      } catch {}
      this.currentObjectUrl = null;
    }
    this.currentAudio = null;
    this.isPlayingAudio = false;
    this.abortController = null;
  }
}

