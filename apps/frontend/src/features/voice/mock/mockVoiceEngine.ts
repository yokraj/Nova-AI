import { SpeechToTextProvider, TextToSpeechProvider } from '../types/voiceSession';
import { MOCK_VOICE_COMMAND_PHRASES, MOCK_VOICE_RESPONSES } from './mockVoiceData';

export class MockSpeechToTextEngine implements SpeechToTextProvider {
  private timer: any = null;

  startListening(onTranscript?: (t: string) => void, onComplete?: (fullT: string) => void) {
    const randomPhrase =
      MOCK_VOICE_COMMAND_PHRASES[Math.floor(Math.random() * MOCK_VOICE_COMMAND_PHRASES.length)];
    const words = randomPhrase.split(' ');
    let index = 0;

    this.timer = setInterval(() => {
      index++;
      const partial = words.slice(0, index).join(' ');
      onTranscript?.(partial);

      if (index >= words.length) {
        clearInterval(this.timer);
        onComplete?.(randomPhrase);
      }
    }, 250);
  }

  stopListening() {
    if (this.timer) {
      clearInterval(this.timer);
    }
  }

  onTranscript(transcript: string) {
    // Optional interface handler
  }
}

export class MockTextToSpeechEngine implements TextToSpeechProvider {
  private timer: any = null;
  private currentProgress = 0;

  speak(text: string, onProgress: (pct: number) => void, onComplete: () => void) {
    this.stop();
    this.currentProgress = 0;

    this.timer = setInterval(() => {
      this.currentProgress += 5;
      onProgress(this.currentProgress);

      if (this.currentProgress >= 100) {
        this.stop();
        onComplete();
      }
    }, 150);
  }

  pause() {
    if (this.timer) clearInterval(this.timer);
  }

  resume() {
    // Resume simulation handled in hook
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    this.currentProgress = 0;
  }
}

export function getMockVoiceResponse(prompt: string): string {
  const lower = prompt.toLowerCase();
  if (lower.includes('quantum')) return MOCK_VOICE_RESPONSES.quantum;
  if (lower.includes('open') || lower.includes('project')) return MOCK_VOICE_RESPONSES.open;
  if (lower.includes('analyze') || lower.includes('code')) return MOCK_VOICE_RESPONSES.analyze;
  if (lower.includes('mission')) return MOCK_VOICE_RESPONSES.mission;
  if (lower.includes('agent')) return MOCK_VOICE_RESPONSES.agents;
  if (lower.includes('light')) return MOCK_VOICE_RESPONSES.lights;
  return MOCK_VOICE_RESPONSES.default;
}
