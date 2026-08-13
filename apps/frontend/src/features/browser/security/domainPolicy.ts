export class DomainPolicy {
  private trustedDomains = ['google.com', 'github.com', 'youtube.com', 'wikipedia.org', 'stackoverflow.com'];

  isTrustedDomain(domainName?: string): boolean {
    if (!domainName) return false;
    const clean = domainName.toLowerCase();
    return this.trustedDomains.some((trusted) => clean === trusted || clean.endsWith(`.${trusted}`));
  }
}
