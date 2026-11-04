/**
 * Synthesized Acoustic Cues and Chimes for JARVIS Voice Interaction.
 * Uses native Web Audio API oscillators to create responsive, futuristic audio feedback
 * with zero network latency and zero asset dependencies.
 */

export class AudioChimeService {
  private audioCtx: AudioContext | null = null;

  private getAudioContext(): AudioContext | null {
    if (typeof window === 'undefined') return null;
    if (!this.audioCtx) {
      const AudioCtxClass = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioCtxClass) {
        this.audioCtx = new AudioCtxClass();
      }
    }
    if (this.audioCtx && this.audioCtx.state === 'suspended') {
      this.audioCtx.resume().catch(() => {});
    }
    return this.audioCtx;
  }

  /**
   * Plays a crisp, futuristic dual-tone ascending chime (587Hz -> 880Hz)
   * signaling that the wake word "Hey Nova" was detected and microphone is active.
   */
  playWakeAcknowledgment(volume: number = 0.25): void {
    const ctx = this.getAudioContext();
    if (!ctx) return;

    try {
      const now = ctx.currentTime;

      // Note 1: D5 (587.33 Hz)
      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(587.33, now);

      gain1.gain.setValueAtTime(0, now);
      gain1.gain.linearRampToValueAtTime(volume * 0.9, now + 0.02);
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.14);

      osc1.connect(gain1);
      gain1.connect(ctx.destination);

      osc1.start(now);
      osc1.stop(now + 0.15);

      // Note 2: A5 (880.00 Hz) - slightly delayed for a pleasant two-step chord
      const osc2 = ctx.createOscillator();
      const gain2 = ctx.createGain();
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(880.0, now + 0.07);

      gain2.gain.setValueAtTime(0, now + 0.07);
      gain2.gain.linearRampToValueAtTime(volume, now + 0.09);
      gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.28);

      osc2.connect(gain2);
      gain2.connect(ctx.destination);

      osc2.start(now + 0.07);
      osc2.stop(now + 0.3);
    } catch (e) {
      console.warn('Could not play wake chime:', e);
    }
  }

  /**
   * Plays a subtle downward tone (600Hz -> 300Hz) when the user interrupts speech.
   */
  playInterruptedTone(volume: number = 0.2): void {
    const ctx = this.getAudioContext();
    if (!ctx) return;

    try {
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(520, now);
      osc.frequency.exponentialRampToValueAtTime(260, now + 0.15);

      gain.gain.setValueAtTime(volume, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.16);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 0.18);
    } catch (e) {
      console.warn('Could not play interrupt tone:', e);
    }
  }

  /**
   * Plays a calm descent chime when conversation is ended (e.g. "Goodbye Nova").
   */
  playSessionEndTone(volume: number = 0.2): void {
    const ctx = this.getAudioContext();
    if (!ctx) return;

    try {
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(783.99, now); // G5
      osc.frequency.setValueAtTime(523.25, now + 0.12); // C5

      gain.gain.setValueAtTime(0, now);
      gain.gain.linearRampToValueAtTime(volume, now + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 0.36);
    } catch (e) {
      console.warn('Could not play session end tone:', e);
    }
  }

  dispose(): void {
    if (this.audioCtx) {
      try {
        this.audioCtx.close();
      } catch {}
      this.audioCtx = null;
    }
  }
}

