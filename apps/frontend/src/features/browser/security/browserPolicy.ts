import { BrowserActionType } from '../types/browserAction';
import { BrowserRiskLevel, BrowserPermission } from '../types/browserPermission';

export class BrowserPolicy {
  getRiskLevel(action: BrowserActionType): BrowserRiskLevel {
    switch (action) {
      case 'OPEN_BROWSER':
      case 'OPEN_TAB':
      case 'NAVIGATE':
      case 'READ_PAGE':
      case 'FIND_TEXT':
      case 'EXTRACT_TEXT':
      case 'EXTRACT_LINKS':
      case 'SCREENSHOT':
        return 'SAFE';

      case 'CLOSE_TAB':
      case 'SWITCH_TAB':
      case 'GO_BACK':
      case 'GO_FORWARD':
      case 'RELOAD':
      case 'SCROLL':
      case 'WAIT_FOR_ELEMENT':
      case 'WAIT_FOR_NAVIGATION':
        return 'LOW';

      case 'CLICK_ELEMENT':
      case 'TYPE_TEXT':
      case 'SELECT_OPTION':
      case 'DOWNLOAD_FILE':
      case 'UPLOAD_FILE':
        return 'MEDIUM';

      default:
        return 'HIGH';
    }
  }

  evaluatePermission(action: BrowserActionType, targetDomain?: string): BrowserPermission {
    const riskLevel = this.getRiskLevel(action);
    const requiresApproval = riskLevel === 'HIGH' || riskLevel === 'CRITICAL';

    return {
      riskLevel,
      requiresApproval,
      reason: requiresApproval
        ? `Browser action "${action}" on domain "${targetDomain || 'web'}" requires explicit user authorization.`
        : `Browser action "${action}" authorized.`,
    };
  }
}
