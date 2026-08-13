import { UrlResolver } from '../resolvers/urlResolver';

export class NavigationGuard {
  private urlResolver = new UrlResolver();
  private blockedSchemes = ['javascript:', 'data:', 'file:', 'vbscript:'];

  validateNavigation(urlInput: string): { safe: boolean; reason?: string; resolvedUrl?: string } {
    if (!urlInput) {
      return { safe: false, reason: 'Empty navigation URL target.' };
    }

    const lower = urlInput.trim().toLowerCase();
    for (const scheme of this.blockedSchemes) {
      if (lower.startsWith(scheme)) {
        return { safe: false, reason: `Navigation blocked: Disallowed scheme "${scheme}".` };
      }
    }

    const resolved = this.urlResolver.resolveUrl(urlInput);
    if (!resolved.valid || !resolved.resolvedUrl) {
      return { safe: false, reason: resolved.error || 'Invalid navigation target.' };
    }

    return { safe: true, resolvedUrl: resolved.resolvedUrl };
  }
}
