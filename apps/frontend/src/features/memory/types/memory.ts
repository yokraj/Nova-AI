export type MemoryCategory =
  | 'Conversation'
  | 'User Preference'
  | 'Project'
  | 'Decision'
  | 'Architecture'
  | 'Task'
  | 'Requirement'
  | 'Document'
  | 'Code'
  | 'Repository'
  | 'Technology'
  | 'Person'
  | 'Agent'
  | 'Mission'
  | 'Device'
  | 'Workflow'
  | 'Fact'
  | 'Instruction';

export type MemoryImportance = 'Low' | 'Normal' | 'High' | 'Critical';

export type MemorySourceOrigin = 'Conversation' | 'Voice' | 'Document' | 'Code' | 'Repository' | 'User instruction' | 'Mission' | 'Agent';

export interface MemorySourceInfo {
  origin: MemorySourceOrigin;
  timestamp: string;
  referenceId?: string;
  confidence: number; // 0.0 to 1.0
}

export interface MemoryItem {
  id: string;
  type: MemoryCategory;
  title: string;
  content: string;
  summary: string;
  createdAt: string;
  updatedAt: string;
  source: MemorySourceInfo;
  importance: MemoryImportance;
  confidence: number;
  tags: string[];
  project: string;
  workspace: string;
  relationships: string[]; // Related entity IDs
  status: 'active' | 'archived' | 'pinned';
}

export interface MemoryConflictItem {
  id: string;
  topic: string;
  memoryA: MemoryItem;
  memoryB: MemoryItem;
  detectedAt: string;
}

export interface MemoryProvider {
  searchMemories: (query: string, filters?: any) => MemoryItem[];
  getMemoryById: (id: string) => MemoryItem | undefined;
  forgetMemory: (id: string) => void;
  resolveConflict: (conflictId: string, resolution: 'keep_a' | 'keep_b' | 'keep_both') => void;
}
