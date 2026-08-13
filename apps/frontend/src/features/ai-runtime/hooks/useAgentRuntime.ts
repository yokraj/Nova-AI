import { useState } from 'react';
import { AgentRuntime } from '../runtime/agentRuntime';
import { AgentState } from '../types/agentState';
import { ExecutionPlan } from '../types/executionPlan';

export function useAgentRuntime() {
  const [runtime] = useState(() => new AgentRuntime());
  const [state, setState] = useState<AgentState>('IDLE');
  const [activePlan, setActivePlan] = useState<ExecutionPlan | null>(null);

  const executeGoal = async (goal: string) => {
    setState('UNDERSTANDING');
    const result = await runtime.executeGoal(goal);
    setState(runtime.getState());
    setActivePlan(runtime.getActivePlan());
    return result;
  };

  const cancelExecution = () => {
    runtime.cancelExecution();
    setState(runtime.getState());
  };

  return {
    executeGoal,
    cancelExecution,
    state,
    activePlan,
  };
}
