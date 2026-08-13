import { FileSystemOperationType } from '../types/fileSystemOperation';

export class FileSystemPolicy {
  getRiskLevel(operation: FileSystemOperationType): 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' {
    switch (operation) {
      case 'READ_DIRECTORY':
      case 'GET_FILE_INFO':
      case 'SEARCH_FILES':
      case 'SEARCH_DIRECTORIES':
      case 'CHECK_EXISTS':
      case 'GET_FILE_SIZE':
      case 'GET_DIRECTORY_SIZE':
      case 'READ_TEXT_FILE':
      case 'FIND_DUPLICATES':
        return 'SAFE';

      case 'CREATE_FILE':
      case 'CREATE_DIRECTORY':
      case 'COPY_FILE':
      case 'COPY_DIRECTORY':
      case 'RENAME_FILE':
      case 'RENAME_DIRECTORY':
        return 'LOW';

      case 'MOVE_FILE':
      case 'MOVE_DIRECTORY':
      case 'WRITE_TEXT_FILE':
        return 'MEDIUM';

      case 'DELETE_FILE':
        return 'HIGH';

      case 'DELETE_DIRECTORY':
        return 'CRITICAL';

      default:
        return 'MEDIUM';
    }
  }

  requiresApproval(operation: FileSystemOperationType): boolean {
    const risk = this.getRiskLevel(operation);
    return risk === 'HIGH' || risk === 'CRITICAL';
  }
}
