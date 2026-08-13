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
  text?: string;
  application?: string;
  windowTitle?: string;
  actionable: boolean;
}
