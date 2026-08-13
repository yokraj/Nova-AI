import { PathSecurity } from '../../file-system/security/pathSecurity';

export class DownloadGuard {
  private pathSecurity = new PathSecurity();

  validateDownload(downloadUrl: string, destinationPath: string): { safe: boolean; reason?: string } {
    if (!downloadUrl) return { safe: false, reason: 'Empty download URL.' };
    if (!destinationPath) return { safe: false, reason: 'Empty destination download path.' };

    const lowerUrl = downloadUrl.toLowerCase();
    if (!lowerUrl.startsWith('https://') && !lowerUrl.startsWith('http://')) {
      return { safe: false, reason: 'Download URL must use HTTP/HTTPS protocol.' };
    }

    const pathCheck = this.pathSecurity.isSafePath(destinationPath);
    if (!pathCheck.safe) {
      return { safe: false, reason: `Download destination rejected: ${pathCheck.reason}` };
    }

    return { safe: true };
  }
}
