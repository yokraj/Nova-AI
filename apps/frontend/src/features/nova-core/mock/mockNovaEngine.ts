import { NovaResponse } from '../types/novaCommand';
import { NovaCoreState, NovaContextDrawerType } from '../types/novaCore';

export interface SimulatedExecutionStep {
  delayMs: number;
  state: NovaCoreState;
  text: string;
  responsePayload?: Partial<NovaResponse>;
}

export function simulateNovaCommandEngine(
  prompt: string,
  onStep: (step: SimulatedExecutionStep) => void,
  onOpenDrawer?: (drawer: NovaContextDrawerType) => void
) {
  const lower = prompt.toLowerCase().trim();

  // Check contextual drawer commands first
  if (lower.includes('show my agents') || lower.includes('view agents') || lower.includes('list agents')) {
    onOpenDrawer?.('agents');
    onStep({
      delayMs: 300,
      state: 'SUCCESS',
      text: 'Opening active workforce agents context...',
      responsePayload: {
        spokenText: 'Here is your active workforce of 67 specialized agents.',
        suggestedDrawer: 'agents',
      },
    });
    return;
  }

  if (lower.includes('show my devices') || lower.includes('check my devices') || lower.includes('view devices')) {
    onOpenDrawer?.('devices');
    onStep({
      delayMs: 300,
      state: 'SUCCESS',
      text: 'Opening cross-platform device mesh context...',
      responsePayload: {
        spokenText: 'Here are your 5 connected mesh nodes.',
        suggestedDrawer: 'devices',
      },
    });
    return;
  }

  if (lower.includes('show my running missions') || lower.includes('view missions') || lower.includes('run a mission')) {
    onOpenDrawer?.('missions');
    onStep({
      delayMs: 300,
      state: 'SUCCESS',
      text: 'Opening autonomous mission control center...',
      responsePayload: {
        spokenText: 'Here are your active DAG execution missions.',
        suggestedDrawer: 'missions',
      },
    });
    return;
  }

  if (lower.includes('what do you remember') || lower.includes('memory') || lower.includes('show memory')) {
    onOpenDrawer?.('memory');
    onStep({
      delayMs: 300,
      state: 'SUCCESS',
      text: 'Retrieving semantic memory store...',
      responsePayload: {
        spokenText: 'Indexed 142,850 memory vectors in workspace Nova-AI.',
        suggestedDrawer: 'memory',
      },
    });
    return;
  }

  // Handling specific simulated prompt scenarios
  if (lower.includes('quantum') || lower.includes('explain')) {
    onStep({ delayMs: 400, state: 'THINKING', text: 'Understanding request intent...' });
    setTimeout(() => {
      onStep({
        delayMs: 800,
        state: 'SPEAKING',
        text: 'Nova Speaking...',
        responsePayload: {
          spokenText:
            'Quantum computing harnesses qubits, superposition, and entanglement to solve complex optimization and cryptographic computations exponentially faster than classical binary architecture.',
          detailedOutput: 'Synthesized quantum physics principles with algorithm complexity theory.',
        },
      });
    }, 800);
    return;
  }

  if (lower.includes('vs code') || lower.includes('open app') || lower.includes('workspace')) {
    onStep({ delayMs: 300, state: 'THINKING', text: 'Parsing OS automation command...' });
    setTimeout(() => {
      onStep({ delayMs: 600, state: 'PLANNING', text: 'Planning application launch sequence...' });
    }, 600);
    setTimeout(() => {
      onStep({ delayMs: 1200, state: 'EXECUTING', text: 'Executing desktop automation macro...' });
    }, 1200);
    setTimeout(() => {
      onStep({
        delayMs: 1800,
        state: 'SUCCESS',
        text: 'Complete.',
        responsePayload: {
          spokenText: 'Visual Studio Code workspace launched successfully.',
          detailedOutput: 'Process ID: 4120 • Path: C:/Projects/Nova-AI',
        },
      });
    }, 1800);
    return;
  }

  if (lower.includes('lights') || lower.includes('turn on') || lower.includes('device control')) {
    onStep({ delayMs: 300, state: 'PLANNING', text: 'Evaluating IoT Smart Home device permission...' });
    setTimeout(() => {
      onStep({
        delayMs: 700,
        state: 'PLANNING',
        text: 'Security Approval Required',
        responsePayload: {
          spokenText: 'Action requires approval: Control Smart Home Lighting Node.',
          securityApprovalRequired: true,
          securityActionTitle: 'Smart Home IoT Light Control (192.168.1.250)',
          securityRiskLevel: 'LOW',
        },
      });
    }, 700);
    return;
  }

  // Default multi-agent mission simulation (e.g. "Analyze my project", "Create a report")
  onStep({ delayMs: 400, state: 'THINKING', text: 'Understanding request...' });
  setTimeout(() => {
    onStep({ delayMs: 800, state: 'PLANNING', text: 'Preparing the best multi-agent approach...' });
  }, 800);
  setTimeout(() => {
    onStep({ delayMs: 1400, state: 'EXECUTING', text: 'Working on it (Solution Architect & Backend Lead assigned)...' });
  }, 1400);
  setTimeout(() => {
    onStep({
      delayMs: 2200,
      state: 'SUCCESS',
      text: 'Done.',
      responsePayload: {
        spokenText: `Completed processing: "${prompt}". Autonomous mission msn_${Math.random().toString(16).substring(2, 7)} delivered cleanly.`,
        assignedAgent: 'Solution Architect',
        missionId: `msn_${Math.random().toString(16).substring(2, 7)}`,
        detailedOutput: 'All subtasks completed with 100% test coverage.',
      },
    });
  }, 2200);
}
