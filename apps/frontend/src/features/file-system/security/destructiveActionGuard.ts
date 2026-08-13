import { FileSystemRequest } from '../types/fileSystemRequest';

export interface DestructiveImpactAssessment {
  isDestructive: boolean;
  requiresApproval: boolean;
  targetPath: string;
  operation: string;
  consequencesMessage: string;
}

export class DestructiveActionGuard {
  assess(request: FileSystemRequest): DestructiveImpactAssessment {
    const isDelete =
      request.operation === 'DELETE_FILE' || request.operation === 'DELETE_DIRECTORY';

    if (!isDelete) {
      return {
        isDestructive: false,
        requiresApproval: request.requiresApproval,
        targetPath: request.primaryTarget.resolvedPath,
        operation: request.operation,
        consequencesMessage: 'Non-destructive file system operation.',
      };
    }

    const isDir = request.operation === 'DELETE_DIRECTORY';

    return {
      isDestructive: true,
      requiresApproval: true,
      targetPath: request.primaryTarget.resolvedPath,
      operation: request.operation,
      consequencesMessage: isDir
        ? `Permanently deletes directory "${request.primaryTarget.resolvedPath}" and all nested files/subfolders.`
        : `Permanently deletes file "${request.primaryTarget.resolvedPath}".`,
    };
  }
}
