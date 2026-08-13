import { KnowledgeEntity, KnowledgeRelationship } from '../types/knowledge';

export const MOCK_KNOWLEDGE_ENTITIES: KnowledgeEntity[] = [
  { id: 'ent-nova', name: 'Nova AI OS', type: 'Project', description: 'Universal Local-First AI Operating System', cluster: 'Core', importance: 10, tags: ['OS', 'AI'] },
  { id: 'ent-nova-core', name: 'Nova Core Visual Identity', type: 'Decision', description: 'Authoritative nova-core.png visual identity', cluster: 'Frontend', importance: 9, tags: ['Visual', 'Orb'] },
  { id: 'ent-frontend', name: 'React/TypeScript Frontend', type: 'Framework', description: 'Vite + React + Tailwind + Framer Motion UI', cluster: 'Frontend', importance: 9, tags: ['React', 'TS'] },
  { id: 'ent-backend', name: 'FastAPI Backend', type: 'Framework', description: 'Python 3.12 + FastAPI microservice architecture', cluster: 'Backend', importance: 9, tags: ['Python', 'FastAPI'] },
  { id: 'ent-ollama', name: 'Ollama Model Host', type: 'Tool', description: 'Local LLM inference manager', cluster: 'Inference', importance: 8, tags: ['Ollama', 'Local LLM'] },
  { id: 'ent-qwen', name: 'Qwen 3 8B', type: 'Technology', description: 'Primary local reasoning model', cluster: 'Inference', importance: 8, tags: ['Model', 'Qwen'] },
  { id: 'ent-vector-memory', name: 'Vector Memory Store', type: 'Database', description: 'Semantic vector indexer for high-dimensional embeddings', cluster: 'Memory', importance: 8, tags: ['Vector', 'Memory'] },
  { id: 'ent-knowledge-graph', name: 'Ontological Knowledge Graph', type: 'Database', description: 'Entity-relationship graph database', cluster: 'Knowledge', importance: 8, tags: ['Graph', 'Ontology'] },
  { id: 'ent-voice-engine', name: 'Voice Interaction Runtime', type: 'Workflow', description: 'Speech-to-Text and Text-to-Speech interaction pipeline', cluster: 'Voice', importance: 8, tags: ['Voice', 'STT', 'TTS'] },
  { id: 'ent-agent-workforce', name: 'Universal Agent Workforce', type: 'Agent', description: '67 Specialized agents across 9 divisions', cluster: 'Agents', importance: 9, tags: ['Agents', 'Multi-Agent'] },
];

export const MOCK_KNOWLEDGE_RELATIONSHIPS: KnowledgeRelationship[] = [
  { id: 'rel-1', sourceId: 'ent-nova', targetId: 'ent-frontend', type: 'contains', description: 'Nova AI OS contains React/TypeScript Frontend app', confidence: 1.0 },
  { id: 'rel-2', sourceId: 'ent-nova', targetId: 'ent-backend', type: 'contains', description: 'Nova AI OS contains FastAPI Backend service', confidence: 1.0 },
  { id: 'rel-3', sourceId: 'ent-frontend', targetId: 'ent-nova-core', type: 'uses', description: 'Frontend uses Nova Core visual orb identity', confidence: 0.98 },
  { id: 'rel-4', sourceId: 'ent-backend', targetId: 'ent-ollama', type: 'connects_to', description: 'Backend connects to local Ollama inference service', confidence: 0.95 },
  { id: 'rel-5', sourceId: 'ent-ollama', targetId: 'ent-qwen', type: 'uses', description: 'Ollama uses Qwen 3 8B model', confidence: 0.95 },
  { id: 'rel-6', sourceId: 'ent-backend', targetId: 'ent-vector-memory', type: 'stores', description: 'Backend stores semantic vectors in Vector Memory Store', confidence: 0.92 },
  { id: 'rel-7', sourceId: 'ent-backend', targetId: 'ent-knowledge-graph', type: 'stores', description: 'Backend stores entities in Ontological Knowledge Graph', confidence: 0.92 },
  { id: 'rel-8', sourceId: 'ent-frontend', targetId: 'ent-voice-engine', type: 'implements', description: 'Frontend implements Voice Interaction Runtime', confidence: 0.90 },
  { id: 'rel-9', sourceId: 'ent-backend', targetId: 'ent-agent-workforce', type: 'executes', description: 'Backend executes Universal Agent Workforce', confidence: 0.96 },
];
