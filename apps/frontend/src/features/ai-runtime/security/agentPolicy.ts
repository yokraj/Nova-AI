export class AgentPolicy {
  private promptInjectionPatterns = [
    /ignore\s+(all\s+)?previous\s+instructions/i,
    /system\s+override/i,
    /delete\s+all\s+files/i,
    /execute\s+command\s+cmd/i,
  ];

  sanitizeUntrustedContent(content: string): { safeContent: string; injectionDetected: boolean } {
    let injectionDetected = false;
    let safeContent = content;

    for (const pattern of this.promptInjectionPatterns) {
      if (pattern.test(safeContent)) {
        injectionDetected = true;
        safeContent = safeContent.replace(pattern, '[UNTRUSTED_CONTENT_FILTERED]');
      }
    }

    return { safeContent, injectionDetected };
  }
}
