import { ModelProvider } from './modelProvider';
import { ModelRequest } from '../types/modelRequest';
import { ModelResponse } from '../types/modelResponse';
import { ExecutionPlan } from '../types/executionPlan';

export class MockModelProvider implements ModelProvider {
  providerName = 'MOCK_MODEL_PROVIDER';

  async isAvailable(): Promise<boolean> {
    return true;
  }

  async generatePlan(goal: string): Promise<ExecutionPlan> {
    const lower = goal.toLowerCase();

    if (lower.includes('novaagenttest') || (lower.includes('desktop') && lower.includes('create'))) {
      return {
        planId: `plan-${Date.now()}`,
        goal,
        steps: [
          {
            id: 'step-1',
            stepNumber: 1,
            title: 'Create NovaAgentTest Directory',
            description: 'Create directory on Desktop',
            status: 'PENDING',
            toolCall: {
              callId: 'call-1',
              toolName: 'filesystem.create_directory',
              arguments: { path: 'c:/Projects/Nova-AI/apps/frontend/.nova_test_sandbox/NovaAgentTest' },
              riskLevel: 'LOW',
            },
          },
          {
            id: 'step-2',
            stepNumber: 2,
            title: 'Create test.txt File',
            description: 'Create text file inside NovaAgentTest',
            status: 'PENDING',
            dependencies: ['step-1'],
            toolCall: {
              callId: 'call-2',
              toolName: 'filesystem.create_file',
              arguments: { path: 'c:/Projects/Nova-AI/apps/frontend/.nova_test_sandbox/NovaAgentTest/test.txt' },
              riskLevel: 'LOW',
            },
          },
          {
            id: 'step-3',
            stepNumber: 3,
            title: 'Write Message into test.txt',
            description: 'Write "Hello Nova Agent" into test.txt',
            status: 'PENDING',
            dependencies: ['step-2'],
            toolCall: {
              callId: 'call-3',
              toolName: 'filesystem.write_file',
              arguments: {
                path: 'c:/Projects/Nova-AI/apps/frontend/.nova_test_sandbox/NovaAgentTest/test.txt',
                content: 'Hello Nova Agent',
              },
              riskLevel: 'LOW',
            },
          },
          {
            id: 'step-4',
            stepNumber: 4,
            title: 'Verify File & Content',
            description: 'Read file from disk and confirm content matches',
            status: 'PENDING',
            dependencies: ['step-3'],
            toolCall: {
              callId: 'call-4',
              toolName: 'filesystem.read_file',
              arguments: { path: 'c:/Projects/Nova-AI/apps/frontend/.nova_test_sandbox/NovaAgentTest/test.txt' },
              riskLevel: 'SAFE',
            },
          },
        ],
        estimatedDurationSeconds: 1.2,
        createdAt: new Date().toISOString(),
      };
    }

    if (lower.includes('vs code') || lower.includes('open app')) {
      return {
        planId: `plan-${Date.now()}`,
        goal,
        steps: [
          {
            id: 'step-1',
            stepNumber: 1,
            title: 'Launch VS Code Process',
            description: 'Open VS Code editor on local workstation',
            status: 'PENDING',
            toolCall: {
              callId: 'call-1',
              toolName: 'application.open',
              arguments: { applicationName: 'VS Code' },
              riskLevel: 'LOW',
            },
          },
          {
            id: 'step-2',
            stepNumber: 2,
            title: 'Verify Process Running',
            description: 'Confirm process is active in OS process list',
            status: 'PENDING',
            dependencies: ['step-1'],
            toolCall: {
              callId: 'call-2',
              toolName: 'application.verify_running',
              arguments: { applicationName: 'VS Code' },
              riskLevel: 'SAFE',
            },
          },
        ],
        estimatedDurationSeconds: 0.8,
        createdAt: new Date().toISOString(),
      };
    }

    if (lower.includes('chrome') || lower.includes('navigate') || lower.includes('example.com')) {
      return {
        planId: `plan-${Date.now()}`,
        goal,
        steps: [
          {
            id: 'step-1',
            stepNumber: 1,
            title: 'Launch Browser',
            description: 'Initialize browser workspace instance',
            status: 'PENDING',
            toolCall: {
              callId: 'call-1',
              toolName: 'browser.open',
              arguments: { url: 'https://example.com' },
              riskLevel: 'LOW',
            },
          },
          {
            id: 'step-2',
            stepNumber: 2,
            title: 'Navigate to Target Domain',
            description: 'Verify URL matched target destination',
            status: 'PENDING',
            dependencies: ['step-1'],
            toolCall: {
              callId: 'call-2',
              toolName: 'browser.navigate',
              arguments: { url: 'https://example.com' },
              riskLevel: 'SAFE',
            },
          },
        ],
        estimatedDurationSeconds: 1.0,
        createdAt: new Date().toISOString(),
      };
    }

    if (lower.includes('screen') || lower.includes('error') || lower.includes('look at')) {
      return {
        planId: `plan-${Date.now()}`,
        goal,
        steps: [
          {
            id: 'step-1',
            stepNumber: 1,
            title: 'Capture Desktop Display',
            description: 'Inspect active window and observe visual targets',
            status: 'PENDING',
            toolCall: {
              callId: 'call-1',
              toolName: 'vision.observe_screen',
              arguments: { source: 'primary-display' },
              riskLevel: 'LOW',
            },
          },
        ],
        estimatedDurationSeconds: 0.6,
        createdAt: new Date().toISOString(),
      };
    }

    // Default multi-step goal plan
    return {
      planId: `plan-${Date.now()}`,
      goal,
      steps: [
        {
          id: 'step-1',
          stepNumber: 1,
          title: 'Inspect Target Environment',
          description: `Analyze requirements for goal: "${goal}"`,
          status: 'PENDING',
          toolCall: {
            callId: 'call-1',
            toolName: 'filesystem.read_directory',
            arguments: { path: 'c:/Projects/Nova-AI/apps/frontend' },
            riskLevel: 'SAFE',
          },
        },
      ],
      estimatedDurationSeconds: 1.0,
      createdAt: new Date().toISOString(),
    };
  }

  async generateResponse(request: ModelRequest): Promise<ModelResponse> {
    return {
      text: '[SIMULATED] Autonomous goal executed and verified successfully.',
      isComplete: true,
    };
  }
}
