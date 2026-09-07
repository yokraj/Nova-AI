export interface PromptInjectionAssessment {
  safe: boolean;
  sanitizedText: string;
  detectedPatterns: string[];
  reason?: string;
}

export class PromptInjectionGuard {
  private injectionPatterns: RegExp[] = [
    /ignore\s+(previous|all)\s+instructions/i,
    /disregard\s+(previous|all)\s+(rules|prompts|instructions)/i,
    /override\s+system\s+(policy|prompt|instructions)/i,
    /bypass\s+(approval|security|permission|guard)/i,
    /delete\s+all\s+files/i,
    /format\s+c:/i,
    /reveal\s+(system\s+prompt|secrets|passwords|tokens|api_key)/i,
    /disable\s+(security|protection|approval|permissions)/i,
    /sudo\s+rm\s+-rf/i,
  ];

  assessAndSanitize(input: string): PromptInjectionAssessment {
    if (!input) {
      return { safe: true, sanitizedText: '', detectedPatterns: [] };
    }

    const detected: string[] = [];
    for (const pattern of this.injectionPatterns) {
      if (pattern.test(input)) {
        detected.push(pattern.source);
      }
    }

    if (detected.length > 0) {
      let sanitized = input;
      for (const pattern of this.injectionPatterns) {
        sanitized = sanitized.replace(pattern, '[REDACTED_UNTRUSTED_INSTRUCTION]');
      }

      return {
        safe: false,
        sanitizedText: sanitized,
        detectedPatterns: detected,
        reason: `Untrusted prompt injection pattern detected (${detected.length} match(es)). Content sanitized.`,
      };
    }

    return {
      safe: true,
      sanitizedText: input,
      detectedPatterns: [],
    };
  }
}

export const promptInjectionGuard = new PromptInjectionGuard();
