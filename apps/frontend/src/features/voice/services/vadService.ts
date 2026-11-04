/**
 * Real-Time Voice Activity Detection (VAD) Service for Nova-AI.
 * Evaluates microphone stream energy (RMS in dBFS) with adaptive noise tracking
 * and hysteresis hangover windowing to detect speech starts, pauses, and speech completion hands-free.
 */

export type VADSensitivity = 'low' | 'medium' | 'high';

export interface VADOptions {
  sensitivity?: VADSensitivity;
  speechStartMinFrames?: number; // Consecutive speech frames to confirm speech (~60-100ms)
  silenceHangoverMs?: number;    // Milliseconds of silence to confirm end of speech
  onSpeechStart?: () => void;
  onSpeechEnd?: () => void;
  onVolumeChange?: (normalizedLevel: number) => void;
}

export class VoiceActivityDetector {
  private audioCtx: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private sourceNode: MediaStreamAudioSourceNode | null = null;
  private animFrameId: number | null = null;

  private isRunning = false;
  private isSpeaking = false;
  private consecutiveSpeechFrames = 0;
  private silenceStartTimestamp: number | null = null;

  // Thresholds based on sensitivity
  private speechThresholdDb: number;
  private silenceHangoverMs: number;
  private speechStartMinFrames: number;

  private onSpeechStart?: () => void;
  private onSpeechEnd?: () => void;
  private onVolumeChange?: (normalizedLevel: number) => void;

  constructor(options: VADOptions = {}) {
    this.speechThresholdDb = this.resolveSensitivityDb(options.sensitivity || 'medium');
    this.silenceHangoverMs = options.silenceHangoverMs || 1200;
    this.speechStartMinFrames = options.speechStartMinFrames || 3;
    this.onSpeechStart = options.onSpeechStart;
    this.onSpeechEnd = options.onSpeechEnd;
    this.onVolumeChange = options.onVolumeChange;
  }

  private resolveSensitivityDb(sensitivity: VADSensitivity): number {
    switch (sensitivity) {
      case 'high':
        return -48.0; // Captures whisper or quiet speech
      case 'low':
        return -36.0; // Requires louder, deliberate speech in noisy rooms
      case 'medium':
      default:
        return -42.0; // Balanced default
    }
  }

  setSensitivity(sensitivity: VADSensitivity): void {
    this.speechThresholdDb = this.resolveSensitivityDb(sensitivity);
  }

  setSilenceHangoverMs(ms: number): void {
    this.silenceHangoverMs = ms;
  }

  /**
   * Starts real-time acoustic analysis on the provided active MediaStream.
   */
  start(stream: MediaStream): void {
    this.stop();

    if (!stream || !stream.active) {
      console.warn('Cannot start VAD on inactive stream.');
      return;
    }

    try {
      const AudioCtxClass = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtxClass) return;

      this.audioCtx = new AudioCtxClass();
      if (this.audioCtx.state === 'suspended') {
        this.audioCtx.resume().catch(() => {});
      }

      this.sourceNode = this.audioCtx.createMediaStreamSource(stream);
      this.analyser = this.audioCtx.createAnalyser();
      this.analyser.fftSize = 512;
      this.analyser.smoothingTimeConstant = 0.3;

      this.sourceNode.connect(this.analyser);
      this.isRunning = true;
      this.isSpeaking = false;
      this.consecutiveSpeechFrames = 0;
      this.silenceStartTimestamp = null;

      this.processLoop();
    } catch (err) {
      console.error('Failed to initialize VAD audio pipeline:', err);
    }
  }

  private processLoop = (): void => {
    if (!this.isRunning || !this.analyser) return;

    const buffer = new Float32Array(this.analyser.fftSize);
    this.analyser.getFloatTimeDomainData(buffer);

    // Compute Root Mean Square (RMS)
    let sumSq = 0;
    for (let i = 0; i < buffer.length; i++) {
      sumSq += buffer[i] * buffer[i];
    }
    const rms = Math.sqrt(sumSq / buffer.length);

    // Convert to dBFS (relative to 1.0)
    const db = 20 * Math.log10(rms + 1e-6);

    // Normalized volume level (0.0 to 1.0) for visualizer pulse
    const minDb = -65.0;
    const maxDb = -15.0;
    const normalized = Math.max(0, Math.min(1, (db - minDb) / (maxDb - minDb)));

    if (this.onVolumeChange) {
      this.onVolumeChange(normalized);
    }

    const now = performance.now();

    if (db >= this.speechThresholdDb) {
      // Speech energy detected in this frame
      this.consecutiveSpeechFrames++;
      this.silenceStartTimestamp = null;

      if (!this.isSpeaking && this.consecutiveSpeechFrames >= this.speechStartMinFrames) {
        this.isSpeaking = true;
        if (this.onSpeechStart) {
          this.onSpeechStart();
        }
      }
    } else {
      // Frame is below speech threshold (silence/ambient floor)
      this.consecutiveSpeechFrames = 0;

      if (this.isSpeaking) {
        if (this.silenceStartTimestamp === null) {
          this.silenceStartTimestamp = now;
        } else if (now - this.silenceStartTimestamp >= this.silenceHangoverMs) {
          // Sustained silence confirmed after user was speaking -> speech ended!
          this.isSpeaking = false;
          this.silenceStartTimestamp = null;
          if (this.onSpeechEnd) {
            this.onSpeechEnd();
          }
        }
      }
    }

    this.animFrameId = requestAnimationFrame(this.processLoop);
  };

  stop(): void {
    this.isRunning = false;
    this.isSpeaking = false;
    this.consecutiveSpeechFrames = 0;
    this.silenceStartTimestamp = null;

    if (this.animFrameId !== null) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }

    if (this.sourceNode) {
      try {
        this.sourceNode.disconnect();
      } catch {}
      this.sourceNode = null;
    }

    if (this.analyser) {
      try {
        this.analyser.disconnect();
      } catch {}
      this.analyser = null;
    }

    if (this.audioCtx) {
      try {
        this.audioCtx.close();
      } catch {}
      this.audioCtx = null;
    }
  }

  isCurrentlySpeaking(): boolean {
    return this.isSpeaking;
  }
}

