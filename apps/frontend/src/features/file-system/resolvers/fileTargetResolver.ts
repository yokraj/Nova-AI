import { FileSystemTarget } from '../types/fileSystemTarget';
import { PathResolver } from './pathResolver';

export class FileTargetResolver {
  private pathResolver = new PathResolver();

  resolveTarget(rawTarget: string, baseDir?: string): FileSystemTarget {
    const resolvedPath = this.pathResolver.resolve(rawTarget, baseDir);
    const isSpecialFolder =
      resolvedPath.endsWith('/Desktop') ||
      resolvedPath.endsWith('/Documents') ||
      resolvedPath.endsWith('/Downloads') ||
      resolvedPath.endsWith('/Pictures');

    const extMatch = resolvedPath.match(/\.([a-zA-Z0-9]+)$/);
    const extension = extMatch ? extMatch[1] : undefined;

    return {
      rawTarget,
      resolvedPath,
      isSpecialFolder,
      specialFolderName: isSpecialFolder ? resolvedPath.split('/').pop() : undefined,
      extension,
    };
  }
}
