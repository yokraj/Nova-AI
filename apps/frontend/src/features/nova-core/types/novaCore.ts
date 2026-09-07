export type NovaCoreState =
  | 'IDLE'
  | 'LISTENING'
  | 'THINKING'
  | 'PLANNING'
  | 'EXECUTING'
  | 'AWAITING_APPROVAL'
  | 'COMPLETED'
  | 'FAILED'
  | 'SPEAKING'
  | 'SUCCESS'
  | 'ERROR';

export type NovaVoiceState =
  | 'MIC_READY'
  | 'LISTENING'
  | 'PROCESSING'
  | 'NOVA_SPEAKING'
  | 'STOPPED';

export type NovaExecutionStage =
  | 'UNDERSTANDING'
  | 'PLANNING'
  | 'SECURITY_APPROVAL'
  | 'ASSIGNING_AGENTS'
  | 'EXECUTING'
  | 'COMPLETE';

export type NovaContextDrawerType =
  | 'none'
  | 'agents'
  | 'missions'
  | 'devices'
  | 'memory'
  | 'knowledge'
  | 'automation'
  | 'telemetry'
  | 'notifications';

export interface NovaCoreStatusInfo {
  state: NovaCoreState;
  primaryLabel: string;
  subText: string;
  glowColor: string;
  accentBorder: string;
}
