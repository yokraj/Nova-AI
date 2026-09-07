import React, { useState, useEffect } from 'react';
import { Network, Search } from 'lucide-react';
import { MOCK_KNOWLEDGE_ENTITIES, MOCK_KNOWLEDGE_RELATIONSHIPS } from '../mock/mockKnowledgeData';
import { KnowledgeEntity } from '../types/knowledge';
import KnowledgeEntityCard from './KnowledgeEntityCard';
import KnowledgeGraphView from './KnowledgeGraphView';
import KnowledgePathExplanationModal from './KnowledgePathExplanationModal';
import { knowledgeApiService } from '../../../services/api/knowledgeApiService';
import { PersistenceStatusIndicator, PersistenceState } from '../../../components/PersistenceStatusIndicator';

export const KnowledgeWorkspace: React.FC = () => {
  const [entities, setEntities] = useState<KnowledgeEntity[]>(MOCK_KNOWLEDGE_ENTITIES);
  const [relationships] = useState(MOCK_KNOWLEDGE_RELATIONSHIPS);
  const [search, setSearch] = useState('');
  const [selectedEntity, setSelectedEntity] = useState<KnowledgeEntity | null>(null);
  const [persistenceState, setPersistenceState] = useState<PersistenceState>('OFFLINE');

  useEffect(() => {
    let isMounted = true;
    async function loadEntities() {
      setPersistenceState('SYNCING');
      try {
        const remote = await knowledgeApiService.listEntities();
        if (isMounted && remote && remote.length > 0) {
          const mapped: KnowledgeEntity[] = remote.map((r) => ({
            id: r.id,
            name: r.name,
            type: r.entityType as any || 'SystemComponent',
            description: r.description || '',
            importance: 0.9,
            properties: { workspace: r.workspace, project: r.project },
            cluster: 'BackendCore',
            tags: [r.entityType || 'BackendCore'],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          }));
          setEntities(mapped);
          setPersistenceState('PERSISTED');
        } else if (isMounted) {
          setPersistenceState('OFFLINE');
        }
      } catch (err) {
        if (isMounted) setPersistenceState('OFFLINE');
      }
    }
    loadEntities();
    return () => {
      isMounted = false;
    };
  }, []);

  const filtered = entities.filter((e) =>
    e.name.toLowerCase().includes(search.toLowerCase()) ||
    e.description.toLowerCase().includes(search.toLowerCase()) ||
    e.type.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6 pb-12">
      {/* Header Stat Panel */}
      <div className="p-6 rounded-3xl bg-slate-900/90 border border-cyan-500/30 flex flex-col md:flex-row items-center justify-between gap-4 shadow-2xl">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Network className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Nova Knowledge Graph</h1>
            <p className="text-xs text-slate-400 font-mono">
              Ontological entity-relationship graph • 12,480 entities & 48,200 relationships
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 font-mono text-xs">
          <PersistenceStatusIndicator status={persistenceState} />
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-cyan-400 font-bold">12,480</span> Nodes
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-purple-400 font-bold">48,200</span> Edges
          </div>
        </div>
      </div>

      {/* Natural Language Knowledge Search */}
      <div className="relative max-w-2xl">
        <Search className="w-4 h-4 text-slate-500 absolute left-3.5 top-3" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search Knowledge Graph (e.g. 'How is Nova Core connected to frontend?')..."
          className="w-full bg-slate-950 border border-slate-800 rounded-2xl py-2.5 pl-10 pr-4 text-xs text-slate-100 placeholder-slate-500 font-sans focus:outline-none focus:border-cyan-500/50"
        />
      </div>

      {/* Visual Graph Section */}
      <KnowledgeGraphView
        entities={filtered}
        relationships={relationships}
        onSelectEntity={(e) => setSelectedEntity(e)}
      />

      {/* Entity Cards Grid */}
      <div className="space-y-3">
        <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">
          Indexed Entities ({filtered.length})
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((entity) => (
            <KnowledgeEntityCard
              key={entity.id}
              entity={entity}
              onSelect={() => setSelectedEntity(entity)}
            />
          ))}
        </div>
      </div>

      {/* Path Explanation Modal */}
      <KnowledgePathExplanationModal
        entity={selectedEntity}
        onClose={() => setSelectedEntity(null)}
      />
    </div>
  );
};

export default KnowledgeWorkspace;
