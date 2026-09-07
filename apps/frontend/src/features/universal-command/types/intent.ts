export type IntentCategory =
  | 'GENERAL_QUESTION'
  | 'CONVERSATION'
  | 'RESEARCH'
  | 'MEMORY_SEARCH'
  | 'KNOWLEDGE_QUERY'
  | 'CODE_TASK'
  | 'FILE_OPERATION'
  | 'APPLICATION_CONTROL'
  | 'SYSTEM_CONTROL'
  | 'DEVICE_CONTROL'
  | 'PHONE_CONTROL'
  | 'SMART_HOME_CONTROL'
  | 'AGENT_TASK'
  | 'MISSION_REQUEST'
  | 'AUTOMATION_REQUEST'
  | 'VISION_ANALYSIS'
  | 'SETTINGS'
  | 'SKILL_MANAGEMENT'
  | 'UNKNOWN';

export interface IntentClassification {
  category: IntentCategory;
  confidence: number;
  extractedTarget?: string;
  extractedAction?: string;
  extractedParameters?: Record<string, string>;
}

