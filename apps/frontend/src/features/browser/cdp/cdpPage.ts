import { CdpClient } from './cdpClient';
import { CDPTargetResolver, TargetResolutionResult } from './cdpTargetResolver';
import { CdpStructuredPage } from '../types/cdpTypes';

export class CdpPage {
  private client = new CdpClient();
  private targetResolver = new CDPTargetResolver();

  async inspectCurrentPage(tabId?: string): Promise<CdpStructuredPage> {
    const rawPage = await this.client.readDom(tabId);
    
    // Sanitize untrusted webpage text (Prompt Injection Protection)
    const sanitizedText = rawPage.visibleText.map((t) =>
      t.replace(/ignore\s+previous\s+instructions/gi, '[REDACTED_PROMPT_INJECTION]')
    );

    return {
      ...rawPage,
      visibleText: sanitizedText,
    };
  }

  detectSecurityChallenge(page: CdpStructuredPage): { isChallenge: boolean; challengeType?: 'CAPTCHA' | 'MFA' | 'BOT_CHECK'; reason?: string } {
    const fullText = page.visibleText.join(' ').toLowerCase();

    if (fullText.includes('recaptcha') || fullText.includes('hcaptcha') || fullText.includes('verify you are human')) {
      return { isChallenge: true, challengeType: 'CAPTCHA', reason: 'CAPTCHA security verification challenge detected on web page.' };
    }
    if (fullText.includes('two-factor authentication') || fullText.includes('enter verification code') || fullText.includes('authenticator app')) {
      return { isChallenge: true, challengeType: 'MFA', reason: 'Multi-factor authentication (MFA) verification required.' };
    }
    return { isChallenge: false };
  }

  resolveTarget(query: string, page: CdpStructuredPage, preferredSelector?: string): TargetResolutionResult {
    return this.targetResolver.resolveTarget(query, page, preferredSelector);
  }
}
