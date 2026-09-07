import { useState, useCallback } from 'react';
import { UniversalCommand, CommandSource } from '../types/command';
import { MockCommandRouter } from '../mock/mockCommandRouter';
import { MockExecutionEngine } from '../mock/mockExecutionEngine';
import { AgentRuntime } from '../../ai-runtime/runtime/agentRuntime';

export const useUniversalCommand = () => {
  const [router] = useState(() => new MockCommandRouter());
  const [engine] = useState(() => new MockExecutionEngine());
  const [agentRuntime] = useState(() => new AgentRuntime());
  const [currentCommand, setCurrentCommand] = useState<UniversalCommand | null>(null);
  const [commandHistory, setCommandHistory] = useState<UniversalCommand[]>([]);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [drawerDomain, setDrawerDomain] = useState<string | null>(null);

  const processCommand = useCallback(
    async (rawInput: string, source: CommandSource = 'TEXT') => {
      // Step 1: Route Command (Understanding, Intent, Capability, Permission & Risk, Plan)
      const cmd = router.routeCommand(rawInput, source);
      setCurrentCommand(cmd);

      // Check if command is requesting a subsystem view
      const lower = rawInput.toLowerCase();
      if (lower.includes('show agent') || lower.includes('view agent')) {
        setDrawerDomain('agents');
        setIsDrawerOpen(true);
      } else if (lower.includes('show mission') || lower.includes('view mission')) {
        setDrawerDomain('missions');
        setIsDrawerOpen(true);
      } else if (lower.includes('show device') || lower.includes('view device')) {
        setDrawerDomain('device-control');
        setIsDrawerOpen(true);
      } else if (lower.includes('show memory') || lower.includes('view memory')) {
        setDrawerDomain('memory');
        setIsDrawerOpen(true);
      }

      // Step 2: Canonical Real AI Execution via AgentRuntime
      try {
        const agentResult = await agentRuntime.executeGoal(rawInput);
        const updatedCmd: UniversalCommand = {
          ...cmd,
          executionState: agentResult.success ? 'COMPLETED' : 'FAILED',
          result: {
            success: agentResult.success,
            message: agentResult.summary,
            durationSeconds: 0.5,
          },
        };
        setCurrentCommand(updatedCmd);
        setCommandHistory((prev) => [updatedCmd, ...prev]);
      } catch {
        // Fallback to engine if runtime throws
        if (!cmd.permission?.requiresApproval) {
          const executed = await engine.executeCommand(cmd);
          setCurrentCommand(executed);
          setCommandHistory((prev) => [executed, ...prev]);
        }
      }
    },
    [router, engine, agentRuntime]
  );

  const approveCurrentCommand = useCallback(async () => {
    if (!currentCommand) return;
    const approvedCmd = { ...currentCommand, executionState: 'UNDERSTANDING' as const };
    const executed = await engine.executeCommand(approvedCmd);
    setCurrentCommand(executed);
    setCommandHistory((prev) => [executed, ...prev]);
  }, [currentCommand, engine]);

  const openDrawer = (domain?: string) => {
    if (domain) setDrawerDomain(domain);
    setIsDrawerOpen(true);
  };

  const closeDrawer = () => {
    setIsDrawerOpen(false);
  };

  return {
    currentCommand,
    commandHistory,
    processCommand,
    approveCurrentCommand,
    isDrawerOpen,
    drawerDomain,
    openDrawer,
    closeDrawer,
  };
};

export default useUniversalCommand;
