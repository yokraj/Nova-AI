export type DeviceType =
  | 'DESKTOP'
  | 'LAPTOP'
  | 'PHONE'
  | 'TABLET'
  | 'SMART_TV'
  | 'SMART_LIGHT'
  | 'SPEAKER'
  | 'WEARABLE'
  | 'IOT'
  | 'SERVER'
  | 'BROWSER'
  | 'APPLICATION';

export type DeviceStatus =
  | 'ONLINE'
  | 'OFFLINE'
  | 'CONNECTING'
  | 'DISCONNECTED'
  | 'BUSY'
  | 'LOCKED'
  | 'PERMISSION_REQUIRED'
  | 'UNKNOWN';

export type DeviceTrustState =
  | 'TRUSTED'
  | 'UNTRUSTED'
  | 'VERIFICATION_REQUIRED'
  | 'PERMISSION_RESTRICTED'
  | 'BLOCKED';

export interface DeviceItem {
  id: string;
  name: string;
  type: DeviceType;
  platform: string; // e.g. "Windows 11", "Android 14", "Tizen OS"
  status: DeviceStatus;
  trustState: DeviceTrustState;
  connection: 'SECURE' | 'LOCAL_SUBNET' | 'BLUETOOTH' | 'DISCONNECTED';
  capabilities: string[];
  battery?: number; // 0 to 100
  location?: string;
  lastSeen: string;
}

export interface DeviceProvider {
  listDevices: () => DeviceItem[];
  getDeviceById: (id: string) => DeviceItem | undefined;
}
