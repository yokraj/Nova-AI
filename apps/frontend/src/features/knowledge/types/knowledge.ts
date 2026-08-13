export type KnowledgeEntityType =
  | 'User'
  | 'Workspace'
  | 'Project'
  | 'Document'
  | 'CodeFile'
  | 'Function'
  | 'Class'
  | 'API'
  | 'Database'
  | 'Technology'
  | 'Framework'
  | 'Language'
  | 'Requirement'
  | 'Decision'
  | 'Agent'
  | 'Tool'
  | 'Workflow'
  | 'Plugin'
  | 'Repository';

export type KnowledgeRelationshipType =
  | 'depends_on'
  | 'implements'
  | 'uses'
  | 'calls'
  | 'references'
  | 'extends'
  | 'contains'
  | 'belongs_to'
  | 'created_by'
  | 'connects_to'
  | 'executes'
  | 'stores';

export interface KnowledgeEntity {
  id: string;
  name: string;
  type: KnowledgeEntityType;
  description: string;
  cluster: string;
  importance: number; // 1 to 10
  tags: string[];
}

export interface KnowledgeRelationship {
  id: string;
  sourceId: string;
  targetId: string;
  type: KnowledgeRelationshipType;
  description: string;
  confidence: number;
}

export interface KnowledgePath {
  nodes: KnowledgeEntity[];
  relationships: KnowledgeRelationship[];
  explanation: string;
}

export interface KnowledgeGraphProvider {
  getEntities: () => KnowledgeEntity[];
  getRelationships: () => KnowledgeRelationship[];
  explainPath: (sourceId: string, targetId: string) => KnowledgePath;
}
