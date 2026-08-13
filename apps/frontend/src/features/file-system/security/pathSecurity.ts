export class PathSecurity {
  private protectedDirectories = [
    'c:/windows',
    'c:/program files',
    'c:/program files (x86)',
    'c:/system32',
    'c:/windows/system32',
    'c:/boot',
    'c:/recovery',
  ];

  isSafePath(targetPath: string): { safe: boolean; reason?: string } {
    if (!targetPath || typeof targetPath !== 'string') {
      return { safe: false, reason: 'Invalid path input.' };
    }

    const clean = targetPath.replace(/\\/g, '/').toLowerCase();

    // Check path traversal attempts
    if (clean.includes('../') || clean.includes('/..') || clean.includes('..\\')) {
      return { safe: false, reason: 'Path traversal (../) is strictly forbidden.' };
    }

    // Check UNC path abuse
    if (clean.startsWith('//') || clean.startsWith('\\\\')) {
      return { safe: false, reason: 'UNC network paths are not allowed.' };
    }

    // Check protected OS directories
    for (const protectedDir of this.protectedDirectories) {
      if (clean === protectedDir || clean.startsWith(`${protectedDir}/`)) {
        return { safe: false, reason: `Access to protected Windows system location "${protectedDir}" is denied.` };
      }
    }

    // Check null-byte or shell metacharacters
    if (/[\0*?"<>|]/.test(targetPath.replace(/^[a-zA-Z]:/, ''))) {
      return { safe: false, reason: 'Invalid Windows filename or shell metacharacters detected.' };
    }

    return { safe: true };
  }
}
