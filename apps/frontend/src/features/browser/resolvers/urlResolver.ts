export class UrlResolver {
  private knownServices: Record<string, string> = {
    youtube: 'https://www.youtube.com',
    google: 'https://www.google.com',
    github: 'https://github.com',
    nova: 'https://github.com/yokraj/Nova-AI',
    'nova repository': 'https://github.com/yokraj/Nova-AI',
    stackoverflow: 'https://stackoverflow.com',
    wikipedia: 'https://www.wikipedia.org',
    reddit: 'https://www.reddit.com',
  };

  resolveUrl(input: string): { valid: boolean; resolvedUrl?: string; error?: string } {
    if (!input || typeof input !== 'string') {
      return { valid: false, error: 'Empty URL input.' };
    }

    const clean = input.trim().toLowerCase();

    // Check for dangerous schemes
    if (clean.startsWith('javascript:') || clean.startsWith('data:') || clean.startsWith('file:')) {
      return { valid: false, error: `Disallowed URL scheme in "${input}". Only http and https are permitted.` };
    }

    // Check known service shortcuts
    for (const [key, val] of Object.entries(this.knownServices)) {
      if (clean === key || clean === `open ${key}` || clean.includes(key)) {
        return { valid: true, resolvedUrl: val };
      }
    }

    // Direct URL handling
    try {
      let candidate = input.trim();
      if (!candidate.startsWith('http://') && !candidate.startsWith('https://')) {
        candidate = `https://${candidate}`;
      }

      const parsed = new URL(candidate);
      if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
        return { valid: false, error: `Invalid protocol "${parsed.protocol}". Only HTTP/HTTPS allowed.` };
      }

      return { valid: true, resolvedUrl: parsed.toString() };
    } catch {
      return { valid: false, error: `Malformed URL string "${input}".` };
    }
  }

  extractDomain(urlStr: string): string {
    try {
      const parsed = new URL(urlStr.startsWith('http') ? urlStr : `https://${urlStr}`);
      return parsed.hostname;
    } catch {
      return 'unknown';
    }
  }
}
