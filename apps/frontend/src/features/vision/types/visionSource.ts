export type VisionSourceType =
  | 'SCREEN'
  | 'CAMERA'
  | 'IMAGE'
  | 'PDF'
  | 'VIDEO_FRAME'
  | 'BROWSER_PAGE';

export interface VisionSource {
  type: VisionSourceType;
  sourceId: string;
  name?: string;
  permission: 'GRANTED' | 'DENIED' | 'NOT_REQUESTED';
  metadata?: Record<string, any>;
}
