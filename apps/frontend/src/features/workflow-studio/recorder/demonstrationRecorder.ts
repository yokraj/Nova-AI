import { RecordingSession, RecordedAction, WorkflowDefinition, WorkflowNode, WorkflowEdge } from '../types/workflowStudio.js';
import { EventNormalizer } from '../normalizer/eventNormalizer.js';
import { promptInjectionGuard } from '../../ai-runtime/security/promptInjectionGuard.js';

export class DemonstrationRecorder {
  private activeSession: RecordingSession | null = null;
  private normalizer = new EventNormalizer();

  private secretPatterns: RegExp[] = [
    /bearer\s+[a-zA-Z0-9_.-]+/i,
    /api[-_]?key\s*[:=]\s*[a-zA-Z0-9_-]+/i,
    /password\s*[:=]\s*\S+/i,
    /sk-[a-zA-Z0-9]{20,}/i,
    /\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b/i, // Credit card pattern
  ];

  startRecording(title: string = 'New Recorded Workflow'): RecordingSession {
    this.activeSession = {
      sessionId: `rec-session-${Date.now()}`,
      title,
      startedAt: new Date().toISOString(),
      isRecording: true,
      recordedActions: [],
      redactedSecretsCount: 0,
    };
    return { ...this.activeSession };
  }

  recordAction(action: Omit<RecordedAction, 'actionId' | 'timestamp'>): RecordedAction | null {
    if (!this.activeSession || !this.activeSession.isRecording) {
      return null;
    }

    let containsSensitiveData = false;
    const sanitizedArgs: Record<string, any> = {};

    // 1. Redact sensitive values from arguments
    if (action.arguments) {
      for (const [key, val] of Object.entries(action.arguments)) {
        if (typeof val === 'string') {
          let strVal = val;
          for (const pattern of this.secretPatterns) {
            if (pattern.test(strVal)) {
              strVal = '[REDACTED_SECRET]';
              containsSensitiveData = true;
              this.activeSession.redactedSecretsCount += 1;
            }
          }
          const injectRes = promptInjectionGuard.assessAndSanitize(strVal);
          sanitizedArgs[key] = injectRes.sanitizedText;
        } else {
          sanitizedArgs[key] = val;
        }
      }
    }

    // 2. Event Normalization
    const semanticTarget =
      action.semanticTarget ||
      this.normalizer.normalizeEventTarget({
        toolName: action.toolName,
        arguments: sanitizedArgs,
        activeApp: action.activeApp,
        windowTitle: action.windowTitle,
      });

    const recorded: RecordedAction = {
      ...action,
      actionId: `act-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
      timestamp: new Date().toISOString(),
      arguments: sanitizedArgs,
      semanticTarget,
      containsSensitiveData,
    };

    this.activeSession.recordedActions.push(recorded);
    return recorded;
  }

  stopRecording(): RecordingSession | null {
    if (!this.activeSession) return null;

    this.activeSession.isRecording = false;
    this.activeSession.endedAt = new Date().toISOString();
    const finishedSession = { ...this.activeSession };
    return finishedSession;
  }

  getActiveSession(): RecordingSession | null {
    return this.activeSession ? { ...this.activeSession } : null;
  }

  convertSessionToWorkflow(session: RecordingSession): WorkflowDefinition {
    const nodes: WorkflowNode[] = [];
    const edges: WorkflowEdge[] = [];

    // Trigger Node
    const triggerNode: WorkflowNode = {
      id: 'node-trigger-1',
      label: `Trigger: ${session.title}`,
      type: 'TRIGGER',
      riskLevel: 'SAFE',
      requiresApproval: false,
      x: 100,
      y: 100,
    };
    nodes.push(triggerNode);

    let prevNodeId = triggerNode.id;
    let currX = 280;
    let currY = 100;

    session.recordedActions.forEach((act, idx) => {
      const nodeId = `node-act-${idx + 1}`;
      const isHighRisk =
        act.toolName.includes('delete') ||
        act.toolName.includes('terminate') ||
        act.toolName.includes('shutdown') ||
        act.toolName.includes('format');

      const node: WorkflowNode = {
        id: nodeId,
        label: `${act.toolName} (${act.capability})`,
        type: act.capability === 'BROWSER_CONTROL' ? 'BROWSER_ACTION' : 'DESKTOP_ACTION',
        capability: act.capability,
        toolName: act.toolName,
        arguments: act.arguments,
        semanticTarget: act.semanticTarget,
        riskLevel: isHighRisk ? 'HIGH' : 'SAFE',
        requiresApproval: isHighRisk,
        expectedState: act.windowTitle || act.activeApp,
        x: currX,
        y: currY,
      };
      nodes.push(node);

      edges.push({
        id: `edge-${prevNodeId}-${nodeId}`,
        sourceNodeId: prevNodeId,
        targetNodeId: nodeId,
      });

      prevNodeId = nodeId;
      currX += 180;
      if ((idx + 1) % 4 === 0) {
        currX = 280;
        currY += 140;
      }
    });

    return {
      id: `wf-${Date.now()}`,
      name: session.title,
      description: `Workflow converted from recorded session (${session.recordedActions.length} steps, ${session.redactedSecretsCount} secrets redacted)`,
      nodes,
      edges,
      variables: [],
      tags: ['RECORDED', 'AUTONOMOUS'],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      version: 1,
      versionsHistory: [],
      trusted: true,
    };
  }
}
