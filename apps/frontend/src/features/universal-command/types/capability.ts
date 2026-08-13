export type UniversalCapabilityType =
  | 'CONVERSATION_ENGINE'
  | 'MEMORY_SYSTEM'
  | 'KNOWLEDGE_GRAPH'
  | 'AGENT_WORKFORCE'
  | 'MISSION_ORCHESTRATOR'
  | 'APPLICATION_CONTROL'
  | 'FILE_SYSTEM'
  | 'SYSTEM_CONTROL'
  | 'DEVICE_CONTROL'
  | 'PHONE_CONTROL'
  | 'SMART_HOME'
  | 'VISION_ENGINE'
  | 'RESEARCH_ENGINE';

export interface ResolvedCapability {
  type: UniversalCapabilityType;
  providerDomain: string;
  name: string;
  description: string;
  iconName: string;
}
