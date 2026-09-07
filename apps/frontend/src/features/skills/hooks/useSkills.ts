import { useState, useEffect, useCallback } from 'react';
import { Skill, SkillFilter, SkillExecutionResult } from '../types/skill';
import { SkillManager } from '../runtime/skillManager';
import { AgentRuntime } from '../../ai-runtime/runtime/agentRuntime';

export function useSkills(runtime?: AgentRuntime) {
  const [manager] = useState(() => new SkillManager());
  const [skills, setSkills] = useState<Skill[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeExecution, setActiveExecution] = useState<SkillExecutionResult | null>(null);

  const refreshSkills = useCallback(async (filter?: SkillFilter) => {
    setLoading(true);
    try {
      const list = await manager.listSkills(filter);
      setSkills(list);
    } catch (err) {
      console.error('Failed to list skills:', err);
    } finally {
      setLoading(false);
    }
  }, [manager]);

  useEffect(() => {
    refreshSkills();
  }, [refreshSkills]);

  const executeSkill = async (skillId: string, variables?: Record<string, any>) => {
    if (!runtime) {
      throw new Error('AgentRuntime instance is required to execute skills.');
    }
    const res = await manager.executeSkill(skillId, variables, runtime);
    setActiveExecution(res);
    await refreshSkills();
    return res;
  };

  const disableSkill = async (id: string) => {
    await manager.disableSkill(id);
    await refreshSkills();
  };

  const enableSkill = async (id: string) => {
    await manager.enableSkill(id);
    await refreshSkills();
  };

  const deleteSkill = async (id: string) => {
    await manager.deleteSkill(id);
    await refreshSkills();
  };

  const createVersion = async (id: string, changes: string, reason: string) => {
    await manager.createVersion(id, changes, reason);
    await refreshSkills();
  };

  const rollbackVersion = async (id: string, version: number) => {
    await manager.rollbackVersion(id, version);
    await refreshSkills();
  };

  return {
    skills,
    loading,
    activeExecution,
    refreshSkills,
    executeSkill,
    disableSkill,
    enableSkill,
    deleteSkill,
    createVersion,
    rollbackVersion,
    manager,
  };
}
