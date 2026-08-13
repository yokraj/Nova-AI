import { SwarmTask, SwarmResult, SwarmEvent, SwarmMessage, SwarmContext } from '../types/swarm';

export class SwarmSynthesizer {
  synthesizeSwarmResult(
    swarmId: string,
    missionId: string,
    goal: string,
    tasks: SwarmTask[],
    context: SwarmContext,
    events: SwarmEvent[],
    messages: SwarmMessage[],
    durationSeconds: number
  ): SwarmResult {
    const completedTasks = tasks.filter((t) => t.state === 'COMPLETED');
    const totalTasks = tasks.length;
    const readinessPercentage = totalTasks > 0 ? Math.round((completedTasks.length / totalTasks) * 100) : 100;
    const success = tasks.every((t) => t.state === 'COMPLETED');

    const findings: string[] = [];
    const recommendations: string[] = [];

    for (const t of completedTasks) {
      if (t.outputSummary) {
        findings.push(`✓ ${t.title}: ${t.outputSummary}`);
      }
    }

    if (readinessPercentage >= 80) {
      recommendations.push('Environment verified ready for production deployment.');
    } else {
      recommendations.push('Resolve pending task warnings before finalizing deployment.');
    }

    if (context.activeWarnings.length > 0) {
      recommendations.push(`Review ${context.activeWarnings.length} active swarm warning(s).`);
    }

    return {
      swarmId,
      missionId,
      goal,
      success,
      status: success ? 'COMPLETED' : 'FAILED',
      readinessPercentage,
      summary: `Swarm execution completed ${completedTasks.length}/${totalTasks} tasks (${readinessPercentage}% readiness) for goal: "${goal}".`,
      tasksCompleted: completedTasks.length,
      totalTasks,
      findings,
      recommendations,
      eventHistory: events,
      messages,
      durationSeconds,
    };
  }
}
