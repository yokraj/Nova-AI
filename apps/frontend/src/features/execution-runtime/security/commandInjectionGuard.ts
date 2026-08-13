export class CommandInjectionGuard {
  private dangerousPatterns = [
    /&&/,
    /;/ ,
    /\|/,
    /`/,
    /\$\(/,
    /\.\./,
    />/,
    /</,
  ];

  isSafe(input: string): boolean {
    if (!input || typeof input !== 'string') return false;
    for (const pattern of this.dangerousPatterns) {
      if (pattern.test(input)) {
        return false;
      }
    }
    return true;
  }
}
