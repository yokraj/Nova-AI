export type FileSystemErrorType =
  | 'PATH_TRAVERSAL_DETECTED'
  | 'PROTECTED_LOCATION'
  | 'INVALID_WINDOWS_PATH'
  | 'COLLISION_CONFLICT'
  | 'DESTRUCTIVE_APPROVAL_REQUIRED'
  | 'FILE_NOT_FOUND'
  | 'DIRECTORY_NOT_FOUND'
  | 'PERMISSION_DENIED';

export interface FileSystemError {
  type: FileSystemErrorType;
  message: string;
  targetPath: string;
}
