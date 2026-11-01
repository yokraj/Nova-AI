import { useState, useCallback } from 'react';
import { UniversalCommand, CommandSource } from '../types/command';
import { MockCommandRouter } from '../mock/mockCommandRouter';
import { MockExecutionEngine } from '../mock/mockExecutionEngine';
import { AgentRuntime } from '../../ai-runtime/runtime/agentRuntime';
import { ToolPermissionGuard } from '../../ai-runtime/security/toolPermissionGuard';
import { APP_CONFIG } from '@/config/app.config';

export const useUniversalCommand = () => {
  const [router] = useState(() => new MockCommandRouter());
  const [engine] = useState(() => new MockExecutionEngine());
  const [agentRuntime] = useState(() => new AgentRuntime());
  const [permissionGuard] = useState(() => new ToolPermissionGuard());

  const [currentCommand, setCurrentCommand] = useState<UniversalCommand | null>(null);
  const [commandHistory, setCommandHistory] = useState<UniversalCommand[]>([]);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [drawerDomain, setDrawerDomain] = useState<string | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  const cancelExecution = useCallback(() => {
    agentRuntime.cancelExecution();
    setIsExecuting(false);
    if (currentCommand) {
      const cancelledCmd: UniversalCommand = {
        ...currentCommand,
        executionState: 'CANCELLED',
        result: {
          success: false,
          message: 'Execution cancelled by operator.',
          durationSeconds: 0.1,
          errorReason: 'USER_CANCELLED',
        },
      };
      setCurrentCommand(cancelledCmd);
      setCommandHistory((prev) => [cancelledCmd, ...prev]);
    }
  }, [agentRuntime, currentCommand]);

  const processCommand = useCallback(
    async (
      rawInput: string,
      source: CommandSource = 'TEXT',
      attachments?: { files?: any[]; vision?: any }
    ) => {
      if (!rawInput.trim()) return;
      setIsExecuting(true);

      // Step 1: Canonical Command Understanding & Plan Routing
      const cmd = router.routeCommand(rawInput, source);
      if (attachments) {
        cmd.context = {
          ...cmd.context,
          attachments: attachments.files || [],
          vision: attachments.vision || null,
        };
      }

      setCurrentCommand(cmd);

      // Check if command is requesting a subsystem navigation view
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

      // Check tool permission guard requirements
      const requiresPermission =
        cmd.permission?.requiresApproval ||
        (cmd.capability?.type === 'SYSTEM_CONTROL' && cmd.permission?.riskLevel === 'HIGH');

      if (requiresPermission) {
        const awaitingCmd: UniversalCommand = {
          ...cmd,
          executionState: 'AWAITING_APPROVAL',
        };
        setCurrentCommand(awaitingCmd);
        setIsExecuting(false);
        return;
      }

      // Step 2: Canonical Real AI Execution
      // If the command is a query, arithmetic, reasoning, or conversation, route to Real Backend Inference
      if (cmd.capability?.type === 'CONVERSATION_ENGINE' || cmd.intent?.category === 'CONVERSATION') {
        try {
          const token = typeof localStorage !== 'undefined' ? localStorage.getItem('nova_auth_token') : null;
          const headers: Record<string, string> = { 'Content-Type': 'application/json' };
          if (token) headers['Authorization'] = `Bearer ${token}`;

          const res = await fetch(`${APP_CONFIG.apiBaseUrl}/inference/chat`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
              prompt: rawInput,
              model: 'qwen3:8b',
              use_deterministic_tools: true,
            }),
          });

          if (res.ok) {
            const data = await res.json();
            const realAnswer = data.content || '';
            const updatedCmd: UniversalCommand = {
              ...cmd,
              executionState: 'COMPLETED',
              result: {
                success: true,
                message: realAnswer,
                durationSeconds: (data.latency_ms || 500) / 1000,
              },
            };
            setCurrentCommand(updatedCmd);
            setCommandHistory((prev) => [updatedCmd, ...prev]);
            setIsExecuting(false);
            return;
          }
        } catch (backendErr) {
          console.warn('Backend inference unavailable for universal command:', backendErr);
        }
      }

      // Step 3: Canonical Autonomous Agent / Native Bridge Execution
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
        // Fallback execution engine if runtime throws
        const executed = await engine.executeCommand(cmd);
        setCurrentCommand(executed);
        setCommandHistory((prev) => [executed, ...prev]);
      } finally {
        setIsExecuting(false);
      }
    },
    [router, engine, agentRuntime]
  );

  const approveCurrentCommand = useCallback(async () => {
    if (!currentCommand) return;
    setIsExecuting(true);

    const approvedCmd: UniversalCommand = {
      ...currentCommand,
      executionState: 'EXECUTING',
    };
    setCurrentCommand(approvedCmd);

    try {
      const agentResult = await agentRuntime.executeGoal(currentCommand.rawInput);
      const finishedCmd: UniversalCommand = {
        ...approvedCmd,
        executionState: agentResult.success ? 'COMPLETED' : 'FAILED',
        result: {
          success: agentResult.success,
          message: agentResult.summary,
          durationSeconds: 0.6,
        },
      };
      setCurrentCommand(finishedCmd);
      setCommandHistory((prev) => [finishedCmd, ...prev]);
    } catch {
      const executed = await engine.executeCommand(approvedCmd);
      setCurrentCommand(executed);
      setCommandHistory((prev) => [executed, ...prev]);
    } finally {
      setIsExecuting(false);
    }
  }, [currentCommand, agentRuntime, engine]);

  const rejectCurrentCommand = useCallback(() => {
    if (!currentCommand) return;
    const deniedCmd: UniversalCommand = {
      ...currentCommand,
      executionState: 'DENIED',
      result: {
        success: false,
        message: 'Command execution authorization was denied by operator.',
        durationSeconds: 0.1,
        errorReason: 'SECURITY_APPROVAL_DENIED',
      },
    };
    setCurrentCommand(deniedCmd);
    setCommandHistory((prev) => [deniedCmd, ...prev]);
    setIsExecuting(false);
  }, [currentCommand]);

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
    isExecuting,
    processCommand,
    approveCurrentCommand,
    rejectCurrentCommand,
    cancelCommand: cancelExecution,
    isDrawerOpen,
    drawerDomain,
    openDrawer,
    closeDrawer,
  };
};

export default useUniversalCommand;
