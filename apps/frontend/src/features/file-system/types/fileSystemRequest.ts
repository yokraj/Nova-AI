import { FileSystemOperationType, CollisionPolicy } from './fileSystemOperation';
import { FileSystemTarget } from './fileSystemTarget';

export interface FileSystemRequest {
  requestId: string;
  operation: FileSystemOperationType;
  primaryTarget: FileSystemTarget;
  secondaryTarget?: FileSystemTarget;
  contentPayload?: string;
  searchFilter?: {
    pattern?: string;
    extension?: string;
    minSizeBytes?: number;
    maxSizeBytes?: number;
    modifiedTimeFilter?: string;
  };
  collisionPolicy?: CollisionPolicy;
  riskLevel: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  requiresApproval: boolean;
  timestamp: string;
}
