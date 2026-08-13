import { BrowserRequest } from '../types/browserRequest';
import { NavigationGuard } from './navigationGuard';
import { DownloadGuard } from './downloadGuard';
import { FormSubmissionGuard } from './formSubmissionGuard';

export class BrowserPermissionGuard {
  private navGuard = new NavigationGuard();
  private downloadGuard = new DownloadGuard();
  private formGuard = new FormSubmissionGuard();

  validateRequest(request: BrowserRequest): { valid: boolean; reason?: string } {
    if (!request || !request.requestId || !request.action) {
      return { valid: false, reason: 'Malformed browser request.' };
    }

    if (request.action === 'NAVIGATE' || request.action === 'OPEN_TAB') {
      const navCheck = this.navGuard.validateNavigation(request.target.url || request.target.rawTarget);
      if (!navCheck.safe) return { valid: false, reason: navCheck.reason };
    }

    if (request.action === 'DOWNLOAD_FILE') {
      const dlCheck = this.downloadGuard.validateDownload(
        request.target.url || request.target.rawTarget,
        request.parameters?.downloadDestination || 'C:/Users/DefaultUser/Downloads/file'
      );
      if (!dlCheck.safe) return { valid: false, reason: dlCheck.reason };
    }

    if (request.action === 'TYPE_TEXT' || request.action === 'CLICK_ELEMENT') {
      const formCheck = this.formGuard.assessFormAction(request.action, request.parameters?.textInput);
      if (formCheck.requiresApproval && !request.requiresApproval) {
        return { valid: false, reason: formCheck.reason };
      }
    }

    return { valid: true };
  }
}
