import { PathSecurity } from '../../file-system/security/pathSecurity';
import { CommandInjectionGuard } from '../../execution-runtime/security/commandInjectionGuard';
import { ExecutableRegistry } from './executableRegistry';
import { NativeBridgeRequest } from '../types/nativeBridgeRequest';

export class BridgeSecurityGuard {
  private pathSecurity = new PathSecurity();
  private commandGuard = new CommandInjectionGuard();
  private execRegistry = new ExecutableRegistry();

  validateRequest(request: NativeBridgeRequest): { valid: boolean; reason?: string } {
    if (!request || !request.requestId || !request.capability) {
      return { valid: false, reason: 'Malformed native bridge request payload.' };
    }

    // Reject arbitrary command execution strings
    if (request.capability === 'APPLICATION_CONTROL') {
      const alias = request.target.applicationAlias || request.target.rawTarget;
      const trusted = this.execRegistry.isTrustedAlias(alias);
      if (!trusted) {
        return {
          valid: false,
          reason: `Application "${alias}" is not in the trusted executable registry. Arbitrary binary paths are forbidden.`,
        };
      }
    }

    // Validate path security for filesystem requests
    if (request.capability === 'FILE_SYSTEM') {
      const targetPath = request.target.resolvedPath || request.target.rawTarget;
      const pSec = this.pathSecurity.isSafePath(targetPath);
      if (!pSec.safe) {
        return { valid: false, reason: pSec.reason };
      }

      if (request.parameters?.destinationPath) {
        const dSec = this.pathSecurity.isSafePath(request.parameters.destinationPath);
        if (!dSec.safe) {
          return { valid: false, reason: dSec.reason };
        }
      }
    }

    // Shell injection guard
    const rawSafe = this.commandGuard.isSafe(request.target.rawTarget);
    if (!rawSafe) {
      return { valid: false, reason: 'Shell injection or unsafe character detected in raw target.' };
    }

    return { valid: true };
  }
}
