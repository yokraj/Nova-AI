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
        goalText: goal,
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

    if (lower.includes('chrome') && lower.includes('python')) {
      return {
        planId: `plan-${Date.now()}`,
        goal,
        goalText: goal,
        steps: [
          {
            id: 'step-1',
            stepNumber: 1,
            title: 'Launch Google Chrome',
            description: 'Open Google Chrome browser',
            status: 'PENDING',
            toolCall: {
              callId: 'call-1',
              toolName: 'application.open',
              arguments: { applicationName: 'Chrome' },
              riskLevel: 'LOW',
            },
          },
          {
            id: 'step-2',
            stepNumber: 2,
            title: 'Navigate & Search for Python',
            description: 'Search for Python in Chrome',
            status: 'PENDING',
            dependencies: ['step-1'],
            toolCall: {
              callId: 'call-2',
              toolName: 'browser.open',
              arguments: { url: 'https://www.google.com/search?q=Python' },
              riskLevel: 'LOW',
            },
          },
        ],
        estimatedDurationSeconds: 1.5,
        createdAt: new Date().toISOString(),
      };
    }

    if (lower.includes('notepad') && (lower.includes('type') || lower.includes('hello nova'))) {
      const isSave = lower.includes('save');
      const desktopPath = `${process.env.USERPROFILE || 'C:/Users/YOKRAJ M S R'}/Desktop/nova_test_f143.txt`.replace(/\\/g, '/');
      const steps: any[] = [
        {
          id: 'step-1',
          stepNumber: 1,
          title: 'Launch Notepad',
          description: 'Open Notepad text editor',
          status: 'PENDING',
          toolCall: {
            callId: 'call-1',
            toolName: 'application.open',
            arguments: { applicationName: 'Notepad' },
            riskLevel: 'LOW',
          },
        },
        {
          id: 'step-2',
          stepNumber: 2,
          title: 'Focus Notepad Window',
          description: 'Bring Notepad to foreground',
          status: 'PENDING',
          dependencies: ['step-1'],
          toolCall: {
            callId: 'call-2',
            toolName: 'computer.focus_window',
            arguments: { windowTitle: 'Notepad' },
            riskLevel: 'SAFE',
          },
        },
        {
          id: 'step-3',
          stepNumber: 3,
          title: 'Type Hello Nova',
          description: 'Type text payload into Notepad',
          status: 'PENDING',
          dependencies: ['step-2'],
          toolCall: {
            callId: 'call-3',
            toolName: 'computer.type_text',
            arguments: { text: 'Hello Nova' },
            riskLevel: 'LOW',
          },
        },
      ];

      if (isSave) {
        steps.push({
          id: 'step-4',
          stepNumber: 4,
          title: 'Save File on Desktop',
          description: 'Save test file to desktop',
          status: 'PENDING',
          dependencies: ['step-3'],
          toolCall: {
            callId: 'call-4',
            toolName: 'filesystem.write_file',
            arguments: { path: desktopPath, content: 'Hello Nova' },
            riskLevel: 'LOW',
          },
        });
      }

      return {
        planId: `plan-${Date.now()}`,
        goal,
        goalText: goal,
        steps,
        estimatedDurationSeconds: 1.5,
        createdAt: new Date().toISOString(),
      };
    }

    if (lower.includes('close notepad')) {
      return {
        planId: `plan-${Date.now()}`,
        goal,
        goalText: goal,
        steps: [
          {
            id: 'step-1',
            stepNumber: 1,
            title: 'Close Notepad Window',
            description: 'Close active Notepad application',
            status: 'PENDING',
            toolCall: {
              callId: 'call-1',
              toolName: 'computer.close_window',
              arguments: { windowTitle: 'Notepad', processName: 'notepad.exe' },
              riskLevel: 'MEDIUM',
            },
          },
        ],
        estimatedDurationSeconds: 0.5,
        createdAt: new Date().toISOString(),
      };
    }

    if (lower.includes('calculator') || lower.includes('calc')) {
      return {
        planId: `plan-${Date.now()}`,
        goal,
        goalText: goal,
        steps: [
          {
            id: 'step-1',
            stepNumber: 1,
            title: 'Launch Calculator',
            description: 'Open Calculator app',
            status: 'PENDING',
            toolCall: {
              callId: 'call-1',
              toolName: 'application.open',
              arguments: { applicationName: 'Calculator' },
              riskLevel: 'LOW',
            },
          },
          {
            id: 'step-2',
            stepNumber: 2,
            title: 'Focus Calculator Window',
            description: 'Bring Calculator window to foreground',
            status: 'PENDING',
            dependencies: ['step-1'],
            toolCall: {
              callId: 'call-2',
              toolName: 'computer.focus_window',
              arguments: { windowTitle: 'Calculator' },
              riskLevel: 'SAFE',
            },
          },

          {
            id: 'step-3',
            stepNumber: 3,
            title: 'Input Calculation 25 * 4',
            description: 'Send math keystrokes 25*4=',
            status: 'PENDING',
            dependencies: ['step-2'],
            toolCall: {
              callId: 'call-3',
              toolName: 'computer.type_text',
              arguments: { text: '25*4=' },
              riskLevel: 'LOW',
            },
          },
        ],
        estimatedDurationSeconds: 1.2,
        createdAt: new Date().toISOString(),
      };
    }


    if (lower.includes('spotify')) {
      return {
        planId: `plan-${Date.now()}`,
        goal,
        goalText: goal,
        steps: [
          {
            id: 'step-1',
            stepNumber: 1,
            title: 'Launch Spotify',
            description: 'Open Spotify desktop app',
            status: 'PENDING',
            toolCall: {
              callId: 'call-1',
              toolName: 'application.open',
              arguments: { applicationName: 'Spotify' },
              riskLevel: 'LOW',
            },
          },
        ],
        estimatedDurationSeconds: 1.0,
        createdAt: new Date().toISOString(),
      };
    }

    if (lower.includes('notepad')) {
      return {
        planId: `plan-${Date.now()}`,
        goal,
        goalText: goal,
        steps: [
          {
            id: 'step-1',
            stepNumber: 1,
            title: 'Launch Notepad',
            description: 'Open Notepad app',
            status: 'PENDING',
            toolCall: {
              callId: 'call-1',
              toolName: 'application.open',
              arguments: { applicationName: 'Notepad' },
              riskLevel: 'LOW',
            },
          },
        ],
        estimatedDurationSeconds: 0.8,
        createdAt: new Date().toISOString(),
      };
    }

    if (lower.includes('vs code') || lower.includes('open app')) {
      return {
        planId: `plan-${Date.now()}`,
        goal,
        goalText: goal,
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
        goalText: goal,
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
        goalText: goal,
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
