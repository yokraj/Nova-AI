export class PrivacyGuard {
  private sensitivePatterns = [
    /password/i,
    /credit card/i,
    /cvv/i,
    /api[-_]?key/i,
    /bearer\s+[a-z0-9._-]+/i,
    /ssn/i,
  ];

  sanitizeText(extractedText?: string): { sanitizedText?: string; containsSensitiveData: boolean; redactedFields: string[] } {
    if (!extractedText) return { containsSensitiveData: false, redactedFields: [] };

    let containsSensitiveData = false;
    const redactedFields: string[] = [];
    let text = extractedText;

    for (const pattern of this.sensitivePatterns) {
      if (pattern.test(text)) {
        containsSensitiveData = true;
        redactedFields.push(pattern.source);
        text = text.replace(pattern, '[REDACTED_SENSITIVE_DATA]');
      }
    }

    return {
      sanitizedText: text,
      containsSensitiveData,
      redactedFields,
    };
  }
}
