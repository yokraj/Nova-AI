import { ExecutionOrchestrator } from '../../execution-runtime/orchestrator/executionOrchestrator';
import { ExecutionRequest } from '../../execution-runtime/types/executionRequest';
import { ExecutionResult } from '../../execution-runtime/types/executionResult';
import { FileSystemOperationType } from '../types/fileSystemOperation';
import { FileSystemPolicy } from '../security/filesystemPolicy';
import { PathResolver } from '../resolvers/pathResolver';
import { DestructiveActionGuard } from '../security/destructiveActionGuard';

export class FileSystemOrchestrator {
  private orchestrator = new ExecutionOrchestrator();
  private policy = new FileSystemPolicy();
  private resolver = new PathResolver();
  private destructiveGuard = new DestructiveActionGuard();

  async processFileSystemCommand(
    commandText: string,
    operation: FileSystemOperationType,
    rawTarget: string,
    destinationTarget?: string,
    contentPayload?: string
  ): Promise<ExecutionResult> {
    const resolvedPath = this.resolver.resolve(rawTarget);
    const resolvedDest = destinationTarget ? this.resolver.resolve(destinationTarget) : undefined;
    const riskLevel = this.policy.getRiskLevel(operation);
    const requiresApproval = this.policy.requiresApproval(operation);

    const request: ExecutionRequest = {
      executionId: `fs-exec-${Date.now()}`,
      commandId: `cmd-fs-${Date.now()}`,
      capability: 'FILE_SYSTEM',
      action: operation,
      target: resolvedPath,
      parameters: {
        destination: resolvedDest,
        content: contentPayload,
        rawInput: commandText,
      },
      requestedBy: 'user',
      workspace: 'default',
      riskLevel,
      policy: requiresApproval ? 'ALLOW_WITH_APPROVAL' : 'ALLOW',
      permissions: ['FILE_SYSTEM'],
      timestamp: new Date().toISOString(),
    };

    return this.orchestrator.execute(request);
  }
}
