import { SpecialFolderResolver } from './specialFolderResolver';

export class PathResolver {
  private specialResolver = new SpecialFolderResolver();

  resolve(rawTarget: string, baseDir?: string): string {
    if (!rawTarget || typeof rawTarget !== 'string') return '';

    const cleanRaw = rawTarget.trim().replace(/\\/g, '/');

    // Check special folder keywords first
    const specialPath = this.specialResolver.resolveSpecialFolder(cleanRaw);
    if (specialPath && !cleanRaw.includes('/')) {
      return specialPath;
    }

    // Check if target combines a special folder phrase e.g. "Projects on my Desktop" -> Desktop/Projects
    const lower = cleanRaw.toLowerCase();
    if (lower.includes(' on my desktop') || lower.includes(' on desktop')) {
      const folderName = cleanRaw.replace(/ on (my )?desktop/i, '').trim();
      const desktop = this.specialResolver.resolveSpecialFolder('desktop');
      return `${desktop}/${folderName}`;
    }

    if (lower.includes(' in downloads') || lower.includes(' inside downloads')) {
      const folderName = cleanRaw.replace(/ (in|inside) downloads/i, '').trim();
      const downloads = this.specialResolver.resolveSpecialFolder('downloads');
      return `${downloads}/${folderName}`;
    }

    if (lower.includes(' in documents') || lower.includes(' inside documents')) {
      const folderName = cleanRaw.replace(/ (in|inside) documents/i, '').trim();
      const docs = this.specialResolver.resolveSpecialFolder('documents');
      return `${docs}/${folderName}`;
    }

    // Absolute path e.g. C:/Projects/...
    if (/^[a-zA-Z]:\//.test(cleanRaw)) {
      return this.normalizePath(cleanRaw);
    }

    // Relative to base directory or workspace root
    const root = baseDir || this.specialResolver.resolveSpecialFolder('project') || 'C:/Projects/Nova-AI';
    return this.normalizePath(`${root}/${cleanRaw}`);
  }

  normalizePath(pathStr: string): string {
    const parts = pathStr.replace(/\\/g, '/').split('/');
    const stack: string[] = [];

    for (const part of parts) {
      if (part === '' || part === '.') continue;
      if (part === '..') {
        if (stack.length > 0 && !stack[stack.length - 1].endsWith(':')) {
          stack.pop();
        }
      } else {
        stack.push(part);
      }
    }

    if (stack.length === 1 && stack[0].endsWith(':')) {
      return `${stack[0]}/`;
    }
    return stack.join('/');
  }
}
