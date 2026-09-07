export type VoiceSkillAction =
  | 'LEARN_WORKFLOW'
  | 'EXECUTE_SKILL'
  | 'SHOW_SKILLS'
  | 'FORGET_SKILL'
  | 'NONE';

export interface VoiceSkillParseResult {
  action: VoiceSkillAction;
  skillNameQuery?: string;
  confidence: number;
}

export class SkillVoiceHandler {
  parseVoiceCommand(transcript: string): VoiceSkillParseResult {
    const lower = transcript.toLowerCase().trim();

    if (lower.includes('learn this workflow') || lower.includes('remember how i do this') || lower.includes('save this as a skill')) {
      return {
        action: 'LEARN_WORKFLOW',
        confidence: 0.98,
      };
    }

    if (lower.includes('show my skills') || lower.includes('list my automation skills') || lower.includes('what skills do you have')) {
      return {
        action: 'SHOW_SKILLS',
        confidence: 0.96,
      };
    }

    if (lower.includes('forget my') || lower.includes('forget this skill') || lower.includes("don't use that skill anymore")) {
      const match = lower.match(/(?:forget my|forget this skill|don't use)\s+(?:the\s+)?([a-z0-9\s]+?)(?:skill|workflow|$)/i);
      return {
        action: 'FORGET_SKILL',
        skillNameQuery: match && match[1] ? match[1].trim() : undefined,
        confidence: 0.92,
      };
    }

    if (lower.includes('use my') || lower.includes('run my') || lower.includes('execute my')) {
      const match = lower.match(/(?:use my|run my|execute my)\s+([a-z0-9\s]+?)(?:skill|workflow|$)/i);
      return {
        action: 'EXECUTE_SKILL',
        skillNameQuery: match && match[1] ? match[1].trim() : undefined,
        confidence: 0.94,
      };
    }

    return {
      action: 'NONE',
      confidence: 0,
    };
  }
}
