import { create } from 'zustand';
import { MemoryItem } from '@/types';
import { MOCK_MEMORY_ITEMS } from '@/mock/mockMemory';

interface MemoryState {
  memories: MemoryItem[];
  filterWorkspace: string;
  setMemories: (memories: MemoryItem[]) => void;
  setWorkspaceFilter: (workspace: string) => void;
}

export const useMemoryStore = create<MemoryState>((set) => ({
  memories: MOCK_MEMORY_ITEMS,
  filterWorkspace: 'Nova',
  setMemories: (memories) => set({ memories }),
  setWorkspaceFilter: (filterWorkspace) => set({ filterWorkspace }),
}));
