export interface CdpTargetTab {
  id: string;
  title: string;
  url: string;
  type: string;
  webSocketDebuggerUrl?: string;
  active: boolean;
}

export interface CdpDomElement {
  id: string;
  tagName: string;
  text: string;
  attributes: Record<string, string>;
  bounds: { x: number; y: number; width: number; height: number };
  confidence: number;
  accessibleName?: string;
  isInteractive: boolean;
}

export interface CdpStructuredPage {
  url: string;
  title: string;
  visibleText: string[];
  elements: CdpDomElement[];
  timestamp: string;
}

export interface CdpActionResult {
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
