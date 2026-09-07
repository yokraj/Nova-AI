export type NativeExecutionStatus =
  | 'COMPLETED'
  | 'FAILED'
  | 'DENIED'
  | 'APPROVAL_REQUIRED'
  | 'INVALID_REQUEST'
  | 'UNSUPPORTED_CAPABILITY'
  | 'TARGET_NOT_FOUND'
  | 'PERMISSION_DENIED'
  | 'TIMEOUT'
  | 'VERIFICATION_FAILED';

export type NativeVerificationState =
  | 'PROCESS_RUNNING'
  | 'DIRECTORY_EXISTS'
  | 'FILE_EXISTS'
  | 'CONTENT_MATCHES'
  | 'TARGET_ABSENT'
  | 'UNVERIFIED'
  | 'VERIFICATION_FAILED'
  | 'TELEMETRY_VERIFIED'
  | 'VOLUME_VERIFIED'
  | 'BRIGHTNESS_VERIFIED'
  | 'NETWORK_VERIFIED'
  | 'WORKSTATION_LOCKED'
  | 'EXECUTION_DISPATCHED'
  | 'SCREENSHOT_CAPTURED'
  | 'MOUSE_VERIFIED'
  | 'KEYBOARD_VERIFIED'
  | 'WINDOW_VERIFIED'
  | 'CLIPBOARD_VERIFIED'
  | 'CDP_CONNECTED'
  | 'CDP_TAB_CREATED'
  | 'CDP_NAVIGATED'
  | 'CDP_DOM_READ'
  | 'CDP_CLICK_VERIFIED'
  | 'CDP_TYPE_VERIFIED'
  | 'CDP_WAIT_VERIFIED';

export interface NativeBridgeFileItem {
  name: string;
  path: string;
  isDirectory: boolean;
  sizeBytes: number;
  modifiedAt: string;
  extension?: string;
}

export interface NativeBridgeResponse {
  requestId: string;
  status: NativeExecutionStatus;
  verification: NativeVerificationState;
  message: string;
  durationSeconds: number;
  resultData?: {
    processId?: number;
    targetPath?: string;
    destinationPath?: string;
    sizeBytes?: number;
    items?: NativeBridgeFileItem[];
    contentOutput?: string;
    exists?: boolean;
    platform?: string;
    arch?: string;
    release?: string;
    uptimeSeconds?: number;
    cpuModel?: string;
    cpuCores?: number;
    totalMemoryBytes?: number;
    freeMemoryBytes?: number;
    usedMemoryPercent?: number;
    drive?: string;
    status?: string;
    isSystemDrive?: boolean;
    isCharging?: boolean;
    percent?: number;
    source?: string;
    volumeLevel?: number;
    isMuted?: boolean;
    brightnessLevel?: number;
    isConnected?: boolean;
    port?: number;
    interfaceCount?: number;
    processes?: string[];
    format?: string;
    width?: number;
    height?: number;
    x?: number;
    y?: number;
    filePath?: string;
    action?: string;
    keyName?: string;
    combination?: string[];
    activeWindow?: { processName: string; title: string; handle?: string; processId?: number; bounds?: { x: number; y: number; width: number; height: number } };
    windows?: { processName: string; title: string; handle?: string; processId?: number }[];
    clipboardContent?: string;
    tabs?: { id: string; title: string; url: string; active: boolean }[];
    activeTab?: { id: string; title: string; url: string };
    url?: string;
    title?: string;
    visibleText?: string[];
    elements?: any[];
    elementFound?: boolean;
    nodeId?: string;
    confidence?: number;
    screenshotPath?: string;
  };

  errorReason?: string;
  timestamp: string;
}
