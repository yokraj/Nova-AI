export class BridgeOriginGuard {
  private allowedOrigins = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
  ];

  getAllowedOrigins(): string[] {
    return [...this.allowedOrigins];
  }

  isAllowedOrigin(originHeader?: string, remoteAddress?: string): boolean {
    // Enforce localhost binding only
    if (
      remoteAddress &&
      remoteAddress !== '127.0.0.1' &&
      remoteAddress !== '::1' &&
      remoteAddress !== '::ffff:127.0.0.1'
    ) {
      return false;
    }

    if (!originHeader) return true; // Direct local calls allowed
    const cleanOrigin = originHeader.trim().toLowerCase();
    return this.allowedOrigins.some(
      (allowed) => cleanOrigin === allowed || cleanOrigin === `${allowed}/`
    );
  }
}
