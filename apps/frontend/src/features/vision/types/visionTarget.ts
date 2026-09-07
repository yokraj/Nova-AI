export type VisualElementType =
  | 'BUTTON'
  | 'TEXT'
  | 'INPUT'
  | 'CHECKBOX'
  | 'ICON'
  | 'IMAGE'
  | 'WINDOW'
  | 'MENU'
  | 'TAB'
  | 'LINK'
  | 'ERROR_MESSAGE'
  | 'DIALOG'
  | 'TABLE'
  | 'FORM'
  | 'CODE_BLOCK';

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface VisionTarget {
  id: string;
  type: VisualElementType;
  label: string;
  confidence: number;
  boundingBox?: BoundingBox;
  center?: { x: number; y: number };
  text?: string;
  application?: string;
  windowTitle?: string;
  actionable: boolean;
  clickable?: boolean;
  source?: 'REAL_OCR_WIN32' | 'LOCAL_VISION_MODEL' | 'SYSTEM_CAPTURE';
  timestamp?: string;
}
