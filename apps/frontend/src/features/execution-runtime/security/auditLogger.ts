import { ExecutionResult } from '../types/executionResult';
import { ExecutionRequest } from '../types/executionRequest';

export interface AuditEvent {
  eventId: string;
  timestamp: string;
  executionId: string;
  principal: string;
  commandId: string;
  capability: string;
  action: string;
  target: string;
  risk: string;
  policy: string;
  resultStatus: string;
  durationSeconds: number;
  error?: string;
}

export class AuditLogger {
  private events: AuditEvent[] = [];

  record(request: ExecutionRequest, result: ExecutionResult): AuditEvent {
    // Sanitize sensitive metadata if present
    const cleanTarget = this.sanitize(request.target);

    const event: AuditEvent = {
      eventId: `audit-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`,
      timestamp: new Date().toISOString(),
      executionId: request.executionId,
      principal: request.requestedBy,
      commandId: request.commandId,
      capability: request.capability,
      action: request.action,
      target: cleanTarget,
      risk: request.riskLevel,
      policy: request.policy,
      resultStatus: result.status,
      durationSeconds: result.durationSeconds,
      error: result.error,
    };

    this.events.unshift(event);
    return event;
  }

  private sanitize(str: string): string {
    if (!str) return str;
    return str.replace(/(password|token|secret|key)=\S+/gi, '$1=***');
  }

  getEvents(): AuditEvent[] {
    return this.events;
  }
}
