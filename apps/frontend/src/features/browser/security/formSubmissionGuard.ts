export class FormSubmissionGuard {
  assessFormAction(actionName: string, textPayload?: string): { requiresApproval: boolean; riskLevel: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'; reason: string } {
    const lower = (actionName + ' ' + (textPayload || '')).toLowerCase();

    if (lower.includes('password') || lower.includes('purchase') || lower.includes('delete account') || lower.includes('payment') || lower.includes('credit card')) {
      return {
        requiresApproval: true,
        riskLevel: 'CRITICAL',
        reason: 'Sensitive security or financial form submission requires explicit user authorization.',
      };
    }

    if (lower.includes('submit') || lower.includes('post') || lower.includes('send message') || lower.includes('publish')) {
      return {
        requiresApproval: true,
        riskLevel: 'HIGH',
        reason: 'External content submission or message posting requires user approval.',
      };
    }

    return {
      requiresApproval: false,
      riskLevel: 'SAFE',
      reason: 'Standard search or text input entry authorized.',
    };
  }
}
