import { ModelRequest } from '../types/modelRequest';
import { ModelResponse } from '../types/modelResponse';
import { ExecutionPlan } from '../types/executionPlan';

export interface ModelProvider {
  providerName: string;
  isAvailable(): Promise<boolean>;
  generatePlan(goal: string): Promise<ExecutionPlan>;
  generateResponse(request: ModelRequest): Promise<ModelResponse>;
}
