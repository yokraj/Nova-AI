import { LocalVisionProvider } from '../../vision/providers/localVisionProvider.js';
import { NativeBridgeClient } from '../../native-bridge/client/nativeBridgeClient.js';

export interface IdempotencyCheckResult {
  completed: boolean;
  reason: string;
  verifiedState: boolean;
  evidence?: any;
}

export class StepIdempotencyEngine {
  private visionProvider = new LocalVisionProvider();
  private nativeClient = new NativeBridgeClient();

  async verifyStepCompletion(step: {
    id: string;
    title: string;
    toolName: string;
    arguments?: Record<string, any>;
    expectedState?: string;
  }): Promise<IdempotencyCheckResult> {
    const args = step.arguments || {};
    const tool = step.toolName.toLowerCase();

    // 1. Directory or File Creation check
    if (tool.includes('create_directory') || tool.includes('create_folder') || tool.includes('mkdir')) {
      const pathStr = args.path || args.directoryPath || args.folderName;
      if (pathStr) {
        try {
          const res = await this.nativeClient.executeNative({
            requestId: `idemp-check-${step.id}`,
            capability: 'FILE_SYSTEM',
            action: 'CHECK_EXISTS',
            target: { rawTarget: pathStr, resolvedPath: pathStr },
            parameters: {},
            authorization: { userId: 'system', sessionToken: 'dev', riskLevel: 'SAFE', isApproved: true },
            timestamp: new Date().toISOString(),
          });
          if (res.status === 'COMPLETED' && (res.verification === 'DIRECTORY_EXISTS' || res.verification === 'FILE_EXISTS')) {
            return {
              completed: true,
              reason: `Directory '${pathStr}' already exists on filesystem via Native Bridge.`,
              verifiedState: true,
              evidence: res,
            };
          }
        } catch {
          // System check fallback
        }
      }
    }

    // 2. File Creation / Write check
    if (tool.includes('create_file') || tool.includes('write_text_file')) {
      const pathStr = args.path || args.filePath;
      if (pathStr) {
        try {
          const res = await this.nativeClient.executeNative({
            requestId: `idemp-check-${step.id}`,
            capability: 'FILE_SYSTEM',
            action: 'CHECK_EXISTS',
            target: { rawTarget: pathStr, resolvedPath: pathStr },
            parameters: {},
            authorization: { userId: 'system', sessionToken: 'dev', riskLevel: 'SAFE', isApproved: true },
            timestamp: new Date().toISOString(),
          });
          if (res.status === 'COMPLETED' && (res.verification === 'FILE_EXISTS' || res.verification === 'CONTENT_MATCHES')) {
            return {
              completed: true,
              reason: `File '${pathStr}' already exists on filesystem via Native Bridge.`,
              verifiedState: true,
              evidence: res,
            };
          }
        } catch {
          // Fallback
        }
      }
    }



    // 3. Application Launch check
    if (tool.includes('open_application') || tool.includes('launch_application')) {
      const appName = args.applicationName || args.appName || args.app;
      if (appName) {
        try {
          const res = await this.nativeClient.executeNative({
            requestId: `idemp-check-${step.id}`,
            capability: 'APPLICATION_CONTROL',
            action: 'VERIFY_APPLICATION_RUNNING',
            target: { rawTarget: appName, applicationAlias: appName },
            parameters: {},
            authorization: { userId: 'system', sessionToken: 'dev', riskLevel: 'SAFE', isApproved: true },
            timestamp: new Date().toISOString(),
          });
          if (res.status === 'COMPLETED') {
            return {
              completed: true,
              reason: `Application '${appName}' is already active in tasklist.`,
              verifiedState: true,
              evidence: res,
            };
          }
        } catch {
          // Fallback
        }
      }
    }

    // 4. Expected Visual Target check
    if (step.expectedState) {
      try {
        const obs = await this.visionProvider.observeScreen();
        const found = obs.detectedTargets.some((t) =>
          t.label.toLowerCase().includes(step.expectedState!.toLowerCase()) ||
          (t.text && t.text.toLowerCase().includes(step.expectedState!.toLowerCase())) ||
          (obs.activeApplication && obs.activeApplication.toLowerCase().includes(step.expectedState!.toLowerCase())) ||
          (obs.activeWindowTitle && obs.activeWindowTitle.toLowerCase().includes(step.expectedState!.toLowerCase()))
        );
        if (found) {
          return {
            completed: true,
            reason: `Expected visual state '${step.expectedState}' confirmed on screen.`,
            verifiedState: true,
            evidence: obs,
          };
        }
      } catch {
        // Fallback
      }
    }

    return {
      completed: false,
      reason: 'Step action not yet completed in environment.',
      verifiedState: false,
    };
  }
}
