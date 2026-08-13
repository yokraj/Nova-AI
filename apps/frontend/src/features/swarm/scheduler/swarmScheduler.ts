import { SwarmTask } from '../types/swarm';

export class SwarmScheduler {
  getReadyTasks(tasks: SwarmTask[]): SwarmTask[] {
    const completedTaskIds = new Set(
      tasks.filter((t) => t.state === 'COMPLETED').map((t) => t.taskId)
    );

    return tasks.filter((t) => {
      if (t.state === 'COMPLETED' || t.state === 'RUNNING' || t.state === 'FAILED' || t.state === 'CANCELLED') {
        return false;
      }
      // Ready if all dependencies are in completedTaskIds
      return t.dependencies.every((depId) => completedTaskIds.has(depId));
    });
  }

  isSwarmComplete(tasks: SwarmTask[]): boolean {
    return tasks.every((t) => t.state === 'COMPLETED' || t.state === 'FAILED' || t.state === 'CANCELLED');
  }

  calculateProgress(tasks: SwarmTask[]): number {
    if (!tasks || tasks.length === 0) return 100;
    const completed = tasks.filter((t) => t.state === 'COMPLETED').length;
    return Math.round((completed / tasks.length) * 100);
  }
}
