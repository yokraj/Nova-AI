import { UniversalCommand } from '../types/command';
import { CommandResult } from '../types/commandResult';
import { ExecutionOrchestrator } from '@/features/execution-runtime/orchestrator/executionOrchestrator';
import { ExecutionRequest } from '@/features/execution-runtime/types/executionRequest';
import { FileSystemOrchestrator } from '@/features/file-system/orchestrator/fileSystemOrchestrator';
import { FileSystemOperationType } from '@/features/file-system/types/fileSystemOperation';
import { BrowserOrchestrator } from '@/features/browser/orchestrator/browserOrchestrator';
import { BrowserActionType } from '@/features/browser/types/browserAction';
import { VisionOrchestrator } from '@/features/vision/orchestrator/visionOrchestrator';
import { AgentRuntime } from '../../ai-runtime/runtime/agentRuntime';

export class MockExecutionEngine {
  private orchestrator = new ExecutionOrchestrator();
  private fileSystemOrchestrator = new FileSystemOrchestrator();
  private browserOrchestrator = new BrowserOrchestrator();
  private visionOrchestrator = new VisionOrchestrator();
  private agentRuntime = new AgentRuntime();

  async executeCommand(command: UniversalCommand): Promise<UniversalCommand> {
    const updated = { ...command };

    if (updated.permission?.requiresApproval && updated.executionState === 'AWAITING_APPROVAL') {
      return updated; // Wait for explicit user confirmation
    }

    updated.executionState = 'EXECUTING';

    const lower = updated.rawInput.toLowerCase();
    const isVision = lower.includes('screen') || lower.includes('look at') || lower.includes('error') || lower.includes('visual') || lower.includes('image') || lower.includes('button');

    if (isVision) {
      const vResult = await this.visionOrchestrator.processVisionCommand(updated.rawInput, 'OBSERVE_SCREEN', updated.rawInput);

      updated.result = {
        success: vResult.success,
        message: vResult.message,
        durationSeconds: vResult.durationSeconds,
        targetDomain: 'conversation',
        targetId: 'Screen Frame',
        errorReason: vResult.errorReason,
      };

      updated.executionState = vResult.success ? 'COMPLETED' : 'FAILED';
      return updated;
    }

    const isBrowser = lower.includes('youtube') || lower.includes('google') || lower.includes('github') || lower.includes('website') || lower.includes('webpage') || lower.includes('http') || lower.includes('www.') || lower.includes('search web');

    if (isBrowser) {
      const bAction: BrowserActionType = lower.includes('search') ? 'TYPE_TEXT' : lower.includes('read') ? 'READ_PAGE' : 'NAVIGATE';
      const bResult = await this.browserOrchestrator.processBrowserCommand(updated.rawInput, bAction, updated.rawInput);

      updated.result = {
        success: bResult.success,
        message: bResult.message,
        durationSeconds: bResult.durationSeconds,
        targetDomain: 'device-control',
        targetId: bResult.targetUrl || updated.rawInput,
        errorReason: bResult.errorReason,
      };

      updated.executionState = bResult.success ? 'COMPLETED' : 'FAILED';
      return updated;
    }

    const category = updated.intent?.category || 'CONVERSATION';

    // Route real execution for FILE_OPERATION to FileSystemOrchestrator / ExecutionOrchestrator
    if (category === 'FILE_OPERATION') {
      const op = (updated.intent?.extractedAction as FileSystemOperationType) || 'READ_DIRECTORY';
      const target = updated.intent?.extractedTarget || updated.rawInput;

      const realResult = await this.fileSystemOrchestrator.processFileSystemCommand(
        updated.rawInput,
        op,
        target
      );

      updated.result = {
        success: realResult.status === 'COMPLETED',
        message: realResult.message,
        durationSeconds: realResult.durationSeconds,
        targetDomain: 'device-control',
        targetId: realResult.target,
        errorReason: realResult.error,
      };

      updated.executionState = realResult.status === 'COMPLETED' ? 'COMPLETED' : 'FAILED';
      return updated;
    }

    // Route real execution for APPLICATION_CONTROL to ExecutionOrchestrator
    if (category === 'APPLICATION_CONTROL') {
      let appTarget = updated.intent?.extractedTarget || updated.rawInput;
      if (lower.startsWith('open ')) {
        appTarget = updated.rawInput.substring(5).trim();
      }

      const execReq: ExecutionRequest = {
        executionId: `exec-${Date.now()}`,
        commandId: updated.id,
        capability: 'APPLICATION_CONTROL',
        action: 'OPEN_APPLICATION',
        target: appTarget,
        requestedBy: 'user',
        workspace: 'default',
        riskLevel: updated.permission?.riskLevel || 'LOW',
        policy: updated.permission?.policy || 'ALLOW',
        permissions: [],
        timestamp: new Date().toISOString(),
      };

      const realResult = await this.orchestrator.execute(execReq);

      updated.result = {
        success: realResult.status === 'COMPLETED',
        message: realResult.message,
        durationSeconds: realResult.durationSeconds,
        targetDomain: 'device-control',
        targetId: realResult.target,
        errorReason: realResult.error,
      };

      updated.executionState = realResult.status === 'COMPLETED' ? 'COMPLETED' : 'FAILED';
      return updated;
    }

    // Default domain execution simulation
    let message = '';
    let duration = 0.8;

    switch (category) {
      case 'SMART_HOME_CONTROL':
        message = `Smart device operation "${updated.rawInput}" executed successfully.`;
        duration = 0.5;
        break;
      case 'MISSION_REQUEST':
        message = `Mission "${updated.rawInput}" initialized with 5 tasks and 3 assigned agents.`;
        duration = 2.1;
        break;
      case 'AGENT_TASK':
        message = `Task delegated to Research Agent. Synthesis in progress.`;
        duration = 1.5;
        break;
      case 'MEMORY_SEARCH':
        message = `Found 4 relevant vector memory items matching "${updated.rawInput}".`;
        duration = 0.6;
        break;
      case 'SYSTEM_CONTROL':
        message = `Host system command "${updated.rawInput}" completed cleanly.`;
        duration = 0.9;
        break;
      default:
        message = `Nova analyzed "${updated.rawInput}" and generated contextual response.`;
        duration = 0.5;
        break;
    }

    const result: CommandResult = {
      success: true,
      message,
      durationSeconds: duration,
      targetDomain: updated.capability?.providerDomain,
      targetId: updated.target,
    };

    updated.result = result;
    updated.executionState = 'COMPLETED';

    return updated;
  }
}
