export interface FileSystemTarget {
  rawTarget: string;
  resolvedPath: string;
  isSpecialFolder: boolean;
  specialFolderName?: string;
  exists?: boolean;
  isDirectory?: boolean;
  sizeBytes?: number;
  extension?: string;
}
