import { ExecutionRequest } from './executionRequest';
import { ExecutionResult } from './executionResult';

export interface CapabilityAdapter {
  capabilityName: string;
  canHandle(request: ExecutionRequest): boolean;
  validate(request: ExecutionRequest): Promise<boolean>;
  execute(request: ExecutionRequest): Promise<ExecutionResult>;
  verify(request: ExecutionRequest): Promise<boolean>;
  describe(request: ExecutionRequest): string;
}
