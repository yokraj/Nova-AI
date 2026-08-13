import { SwarmConflict, ConflictResolutionStrategy } from '../types/swarm';

export class SwarmConflictResolver {
  detectConflict(
    taskId: string,
    topic: string,
    agentAId: string,
    agentAFinding: string,
    agentBId: string,
    agentBFinding: string
  ): SwarmConflict | null {
    if (agentAFinding.toLowerCase().includes('fail') && agentBFinding.toLowerCase().includes('pass')) {
      return {
        conflictId: `conf-${Date.now()}`,
        taskId,
        topic,
        agentAId,
        agentAFinding,
        agentBId,
        agentBFinding,
        resolutionStrategy: 'PRIORITIZE_CONFIDENCE',
        resolvedOutcome: `Resolved conflict on ${topic}: Prioritized verified evidence over assertion.`,
      };
    }
    return null;
  }

  resolveConflict(conflict: SwarmConflict, strategy: ConflictResolutionStrategy): SwarmConflict {
    conflict.resolutionStrategy = strategy;
    switch (strategy) {
      case 'PRIORITIZE_CONFIDENCE':
        conflict.resolvedOutcome = `Conflict resolved by prioritizing higher-confidence empirical test results (${conflict.agentAFinding}).`;
        break;
      case 'REQUIRE_APPROVAL':
        conflict.resolvedOutcome = `Conflict flagged for human operator review (${conflict.topic}).`;
        break;
      default:
        conflict.resolvedOutcome = `Conflict strategy ${strategy} applied.`;
    }
    return conflict;
  }
}
