export type FileVerificationStatus = 'VERIFIED' | 'UNVERIFIED' | 'VERIFICATION_FAILED';

export interface FileItemInfo {
  name: string;
  path: string;
  isDirectory: boolean;
  sizeBytes: number;
  modifiedAt: string;
  extension?: string;
}

export interface FileSystemResult {
  requestId: string;
  success: boolean;
  status:
    | 'SUCCESS'
    | 'FAILED'
    | 'DENIED'
    | 'APPROVAL_REQUIRED'
    | 'NOT_FOUND'
    | 'ALREADY_EXISTS'
    | 'PERMISSION_DENIED'
    | 'INVALID_PATH'
    | 'CONFLICT'
    | 'TIMEOUT'
    | 'PARTIAL_SUCCESS';
  operation: string;
  targetPath: string;
  destinationPath?: string;
  verification: FileVerificationStatus;
  message: string;
  itemsFound?: FileItemInfo[];
  contentOutput?: string;
  durationSeconds: number;
  errorReason?: string;
  timestamp: string;
}
