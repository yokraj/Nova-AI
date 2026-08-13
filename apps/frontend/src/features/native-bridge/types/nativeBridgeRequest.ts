import {
  NativeBridgeCapabilityType,
  NativeApplicationAction,
  NativeFileSystemAction,
  NativeSystemAction,
  NativeComputerAction,
  NativeBrowserCdpAction,
} from './nativeBridgeCapability';

export interface NativeBridgeAuthorization {
  userId: string;
  sessionToken: string;
  riskLevel: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  isApproved: boolean;
}

export interface NativeBridgeTarget {
  rawTarget: string;
  resolvedPath?: string;
  applicationAlias?: string;
  processId?: number;
  x?: number;
  y?: number;
  windowHandle?: string;
  tabId?: string;
  url?: string;
  selector?: string;
}

export interface NativeBridgeRequest {
  requestId: string;
  capability: NativeBridgeCapabilityType;
  action:
    | NativeApplicationAction
    | NativeFileSystemAction
    | NativeSystemAction
    | NativeComputerAction
    | NativeBrowserCdpAction;
  target: NativeBridgeTarget;
  parameters?: {
    destinationPath?: string;
    contentPayload?: string;
    pattern?: string;
    extension?: string;
    timeoutMs?: number;
    volumeLevel?: number;
    brightnessLevel?: number;
    enabledState?: boolean;
    processName?: string;
    textPayload?: string;
    keyName?: string;
    keyCombination?: string[];
    scrollDelta?: number;
    clipboardText?: string;
    cdpPort?: number;
    url?: string;
    tabId?: string;
    selector?: string;
    textQuery?: string;
    optionValue?: string;
    useProfile?: boolean;
  };
  authorization: NativeBridgeAuthorization;
  timestamp: string;
}
