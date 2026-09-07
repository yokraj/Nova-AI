import { Skill, SkillFilter, SkillVersionHistoryItem } from '../types/skill';

export interface SkillProvider {
  createSkill(skillData: Omit<Skill, 'id' | 'createdAt' | 'updatedAt' | 'usageCount' | 'successRate' | 'version' | 'history'>): Promise<Skill>;
  getSkill(id: string): Promise<Skill | undefined>;
  listSkills(filter?: SkillFilter): Promise<Skill[]>;
  searchSkills(query: string): Promise<Skill[]>;
  updateSkill(id: string, updates: Partial<Skill>): Promise<Skill>;
  deleteSkill(id: string): Promise<boolean>;
  recordUsage(id: string, success: boolean, executionDurationMs: number): Promise<void>;
  createVersion(id: string, changes: string, reason: string): Promise<Skill>;
  getSkillHistory(id: string): Promise<SkillVersionHistoryItem[]>;
  rollbackVersion(id: string, version: number): Promise<Skill>;
  clearAllSkills(): Promise<void>;
}

const STORAGE_KEY = 'nova_skills_store_v1';

export class LocalSkillProvider implements SkillProvider {
  private skills: Map<string, Skill> = new Map();

  constructor() {
    this.loadFromStorage();
  }

  private loadFromStorage(): void {
    this.skills.clear();
    if (typeof window !== 'undefined' && typeof window.localStorage !== 'undefined' && window.localStorage) {
      try {
        const raw = window.localStorage.getItem(STORAGE_KEY);
        if (raw) {
          const parsed: Skill[] = JSON.parse(raw);
          parsed.forEach((s) => this.skills.set(s.id, s));
        }
      } catch (err) {
        console.warn('Failed to load skills from localStorage:', err);
      }
    }
  }

  private saveToStorage(): void {
    const list = Array.from(this.skills.values());
    if (typeof window !== 'undefined' && typeof window.localStorage !== 'undefined' && window.localStorage) {
      try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
      } catch (err) {
        console.warn('Failed to save skills to localStorage:', err);
      }
    }
  }


  async createSkill(
    skillData: Omit<Skill, 'id' | 'createdAt' | 'updatedAt' | 'usageCount' | 'successRate' | 'version' | 'history'>
  ): Promise<Skill> {
    const id = `skill-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`;
    const now = new Date().toISOString();

    const newSkill: Skill = {
      ...skillData,
      id,
      version: 1,
      usageCount: 0,
      successRate: 1.0,
      createdAt: now,
      updatedAt: now,
      history: [
        {
          version: 1,
          changes: 'Initial skill creation',
          reason: 'Initial creation from workflow learning engine',
          timestamp: now,
          successRate: 1.0,
          stepsCount: skillData.steps.length,
        },
      ],
    };

    this.skills.set(id, newSkill);
    this.saveToStorage();
    return newSkill;
  }

  async getSkill(id: string): Promise<Skill | undefined> {
    this.loadFromStorage();
    return this.skills.get(id);
  }

  async listSkills(filter?: SkillFilter): Promise<Skill[]> {
    this.loadFromStorage();
    let result = Array.from(this.skills.values());

    if (!filter) return result;

    if (filter.category) {
      result = result.filter((s) => s.category === filter.category);
    }
    if (filter.status) {
      result = result.filter((s) => s.status === filter.status);
    }
    if (filter.tags && filter.tags.length > 0) {
      result = result.filter((s) => filter.tags!.some((t) => s.tags.includes(t)));
    }
    if (filter.searchQuery) {
      const q = filter.searchQuery.toLowerCase();
      result = result.filter(
        (s) =>
          s.name.toLowerCase().includes(q) ||
          s.description.toLowerCase().includes(q) ||
          s.purpose.toLowerCase().includes(q) ||
          s.triggerPatterns.some((tp) => tp.naturalLanguagePattern.toLowerCase().includes(q))
      );
    }

    return result;
  }

  async searchSkills(query: string): Promise<Skill[]> {
    return this.listSkills({ searchQuery: query });
  }

  async updateSkill(id: string, updates: Partial<Skill>): Promise<Skill> {
    const existing = this.skills.get(id);
    if (!existing) {
      throw new Error(`Skill with ID ${id} not found.`);
    }

    const updated: Skill = {
      ...existing,
      ...updates,
      id: existing.id, // Immutable
      createdAt: existing.createdAt, // Immutable
      updatedAt: new Date().toISOString(),
    };

    this.skills.set(id, updated);
    this.saveToStorage();
    return updated;
  }

  async deleteSkill(id: string): Promise<boolean> {
    const removed = this.skills.delete(id);
    if (removed) {
      this.saveToStorage();
    }
    return removed;
  }

  async recordUsage(id: string, success: boolean, _executionDurationMs: number): Promise<void> {
    const skill = this.skills.get(id);
    if (!skill) return;

    const newUsageCount = skill.usageCount + 1;
    // Exponential moving average or simple running average for success rate
    const oldTotalSuccesses = skill.successRate * skill.usageCount;
    const newTotalSuccesses = oldTotalSuccesses + (success ? 1 : 0);
    const newSuccessRate = Number((newTotalSuccesses / newUsageCount).toFixed(2));

    skill.usageCount = newUsageCount;
    skill.successRate = newSuccessRate;
    skill.lastUsedAt = new Date().toISOString();
    skill.updatedAt = new Date().toISOString();

    this.skills.set(id, skill);
    this.saveToStorage();
  }

  async createVersion(id: string, changes: string, reason: string): Promise<Skill> {
    const skill = this.skills.get(id);
    if (!skill) {
      throw new Error(`Skill with ID ${id} not found.`);
    }

    const newVersionNum = skill.version + 1;
    const now = new Date().toISOString();

    const historyItem: SkillVersionHistoryItem = {
      version: newVersionNum,
      changes,
      reason,
      timestamp: now,
      successRate: skill.successRate,
      stepsCount: skill.steps.length,
    };

    const updatedSkill: Skill = {
      ...skill,
      version: newVersionNum,
      updatedAt: now,
      history: [historyItem, ...skill.history],
    };

    this.skills.set(id, updatedSkill);
    this.saveToStorage();
    return updatedSkill;
  }

  async getSkillHistory(id: string): Promise<SkillVersionHistoryItem[]> {
    const skill = this.skills.get(id);
    return skill ? skill.history : [];
  }

  async rollbackVersion(id: string, targetVersion: number): Promise<Skill> {
    const skill = this.skills.get(id);
    if (!skill) {
      throw new Error(`Skill with ID ${id} not found.`);
    }

    const versionItem = skill.history.find((h) => h.version === targetVersion);
    if (!versionItem) {
      throw new Error(`Version ${targetVersion} not found in skill history.`);
    }

    const now = new Date().toISOString();
    const rollbackHistoryItem: SkillVersionHistoryItem = {
      version: skill.version + 1,
      changes: `Rolled back to version ${targetVersion}`,
      reason: `User requested rollback to v${targetVersion}`,
      timestamp: now,
      successRate: skill.successRate,
      stepsCount: skill.steps.length,
    };

    const updated: Skill = {
      ...skill,
      version: skill.version + 1,
      updatedAt: now,
      history: [rollbackHistoryItem, ...skill.history],
    };

    this.skills.set(id, updated);
    this.saveToStorage();
    return updated;
  }

  async clearAllSkills(): Promise<void> {
    this.skills.clear();
    this.saveToStorage();
  }
}
