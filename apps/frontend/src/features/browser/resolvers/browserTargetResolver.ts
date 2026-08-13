import { BrowserTarget } from '../types/browserTarget';
import { UrlResolver } from './urlResolver';

export class BrowserTargetResolver {
  private urlResolver = new UrlResolver();

  resolveTarget(rawInput: string): BrowserTarget {
    const urlRes = this.urlResolver.resolveUrl(rawInput);
    const resolvedUrl = urlRes.valid ? urlRes.resolvedUrl : undefined;
    const domain = resolvedUrl ? this.urlResolver.extractDomain(resolvedUrl) : undefined;

    return {
      rawTarget: rawInput,
      url: resolvedUrl,
      domain,
    };
  }
}
