import { MemoryItem } from '@/types';

export const MOCK_MEMORY_ITEMS: MemoryItem[] = [
  {
    id: 'mem-001',
    type: 'Semantic',
    content: 'User preference: prefers dark mode glassmorphism theme and Python/TypeScript.',
    workspace: 'Nova',
    confidence: 0.98,
    createdAt: '2026-08-03 12:00:00',
  },
  {
    id: 'mem-002',
    type: 'Project',
    content: 'Repository Nova-AI uses FastAPI backend with SQLAlchemy and React frontend.',
    workspace: 'Nova',
    confidence: 0.95,
    createdAt: '2026-08-03 13:15:20',
  },
];
