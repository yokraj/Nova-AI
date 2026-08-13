export type MouseActionType =
  | 'MOVE_MOUSE'
  | 'CLICK'
  | 'DOUBLE_CLICK'
  | 'RIGHT_CLICK'
  | 'MOUSE_DOWN'
  | 'MOUSE_UP'
  | 'SCROLL'
  | 'DRAG';

export type KeyboardActionType =
  | 'TYPE_TEXT'
  | 'PRESS_KEY'
  | 'KEY_COMBINATION'
  | 'KEY_DOWN'
  | 'KEY_UP'
  | 'COPY'
  | 'PASTE'
  | 'CUT'
  | 'SELECT_ALL';

export type WindowActionType =
  | 'LIST_WINDOWS'
  | 'GET_ACTIVE_WINDOW'
  | 'FOCUS_WINDOW'
  | 'MINIMIZE_WINDOW'
  | 'MAXIMIZE_WINDOW'
  | 'RESTORE_WINDOW'
  | 'CLOSE_WINDOW'
  | 'MOVE_WINDOW'
  | 'RESIZE_WINDOW'
  | 'SWITCH_APPLICATION';

export type ScreenActionType =
  | 'SCREENSHOT'
  | 'OBSERVE_SCREEN'
  | 'FIND_TEXT'
  | 'FIND_UI_ELEMENT'
  | 'GET_SCREEN_SIZE';

export type ComputerTargetType =
  | 'TEXT'
  | 'BUTTON'
  | 'INPUT'
  | 'MENU'
  | 'CHECKBOX'
  | 'LINK'
  | 'TAB'
  | 'WINDOW'
  | 'ICON'
  | 'COORDINATE';

export interface ComputerTarget {
  targetType: ComputerTargetType;
  query: string;
  x?: number;
  y?: number;
  confidence?: number;
  windowTitle?: string;
  applicationName?: string;
}

export interface WindowInfo {
  handle: string;
  processName: string;
  title: string;
  x: number;
  y: number;
  width: number;
  height: number;
  isMinimized: boolean;
  isActive: boolean;
}

export interface ScreenObservation {
  screenshotPath?: string;
  width: number;
  height: number;
  activeWindow?: WindowInfo;
  detectedText: string[];
  detectedElements: { label: string; bounds: { x: number; y: number; width: number; height: number }; confidence: number }[];
  confidence: number;
  timestamp: string;
}

export interface ComputerRequest {
  requestId: string;
  action: MouseActionType | KeyboardActionType | WindowActionType | ScreenActionType;
  target?: ComputerTarget;
  textPayload?: string;
  keyCombination?: string[];
  coordinates?: { x: number; y: number };
  windowTitle?: string;
  riskLevel: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  isApproved: boolean;
  timestamp: string;
}

export interface ComputerResult {
  requestId: string;
  action: string;
  success: boolean;
  message: string;
  data?: any;
  errorReason?: string;
  durationSeconds: number;
  verifiedState: boolean;
  timestamp: string;
}
