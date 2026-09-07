import { StructuredToolCall } from '../types/toolCall.js';
import { ToolResult } from '../types/toolResult.js';
import { WindowsFileSystemAdapter } from '../../file-system/adapters/windowsFileSystemAdapter.js';
import { WindowsApplicationAdapter } from '../../execution-runtime/adapters/windowsApplicationAdapter.js';
import { WindowsSystemAdapter } from '../../execution-runtime/adapters/windowsSystemAdapter.js';
import { BrowserOrchestrator } from '../../browser/orchestrator/browserOrchestrator.js';
import { VisionOrchestrator } from '../../vision/orchestrator/visionOrchestrator.js';
import { ExecutionRequest } from '../../execution-runtime/types/executionRequest.js';

export class ToolExecutor {
  private fsAdapter = new WindowsFileSystemAdapter();
  private appAdapter = new WindowsApplicationAdapter();
  private sysAdapter = new WindowsSystemAdapter();
  private browserOrchestrator = new BrowserOrchestrator();
  private visionOrchestrator = new VisionOrchestrator();

  async executeTool(toolCall: StructuredToolCall): Promise<ToolResult> {
    const started = Date.now();
    const { toolName, arguments: args } = toolCall;

    try {
      if (toolName === 'filesystem.create_directory') {
        const req: ExecutionRequest = {
          executionId: `fs-${Date.now()}`,
          commandId: `cmd-${Date.now()}`,
          capability: 'FILE_SYSTEM',
          action: 'CREATE_DIRECTORY',
          target: args.path,
          requestedBy: 'user',
          workspace: 'default',
          riskLevel: 'LOW',
          policy: 'ALLOW',
          permissions: ['FILE_SYSTEM'],
          timestamp: new Date().toISOString(),
        };
        const res = await this.fsAdapter.execute(req);
        return {
          callId: toolCall.callId,
          toolName,
          success: res.status === 'COMPLETED',
          data: { path: res.target },
          errorReason: res.error,
          durationMs: Date.now() - started,
          observationSummary: res.status === 'COMPLETED' ? `Directory created: ${res.target}` : res.error,
          verifiedState: res.status === 'COMPLETED',
        };
      }

      if (toolName === 'filesystem.create_file') {
        const req: ExecutionRequest = {
          executionId: `fs-${Date.now()}`,
          commandId: `cmd-${Date.now()}`,
          capability: 'FILE_SYSTEM',
          action: 'CREATE_FILE',
          target: args.path,
          parameters: { content: '' },
          requestedBy: 'user',
          workspace: 'default',
          riskLevel: 'LOW',
          policy: 'ALLOW',
          permissions: ['FILE_SYSTEM'],
          timestamp: new Date().toISOString(),
        };
        const res = await this.fsAdapter.execute(req);
        return {
          callId: toolCall.callId,
          toolName,
          success: res.status === 'COMPLETED',
          data: { path: res.target },
          errorReason: res.error,
          durationMs: Date.now() - started,
          observationSummary: res.status === 'COMPLETED' ? `File created: ${res.target}` : res.error,
          verifiedState: res.status === 'COMPLETED',
        };
      }

      if (toolName === 'filesystem.write_file') {
        const req: ExecutionRequest = {
          executionId: `fs-${Date.now()}`,
          commandId: `cmd-${Date.now()}`,
          capability: 'FILE_SYSTEM',
          action: 'WRITE_TEXT_FILE',
          target: args.path,
          parameters: { content: args.content || '' },
          requestedBy: 'user',
          workspace: 'default',
          riskLevel: 'LOW',
          policy: 'ALLOW',
          permissions: ['FILE_SYSTEM'],
          timestamp: new Date().toISOString(),
        };
        const res = await this.fsAdapter.execute(req);
        return {
          callId: toolCall.callId,
          toolName,
          success: res.status === 'COMPLETED',
          data: { path: res.target, content: args.content },
          errorReason: res.error,
          durationMs: Date.now() - started,
          observationSummary: res.status === 'COMPLETED' ? `Wrote content to file: ${res.target}` : res.error,
          verifiedState: res.status === 'COMPLETED',
        };
      }

      if (toolName === 'filesystem.read_file') {
        const req: ExecutionRequest = {
          executionId: `fs-${Date.now()}`,
          commandId: `cmd-${Date.now()}`,
          capability: 'FILE_SYSTEM',
          action: 'READ_TEXT_FILE',
          target: args.path,
          requestedBy: 'user',
          workspace: 'default',
          riskLevel: 'SAFE',
          policy: 'ALLOW',
          permissions: ['FILE_SYSTEM'],
          timestamp: new Date().toISOString(),
        };
        const res = await this.fsAdapter.execute(req);
        return {
          callId: toolCall.callId,
          toolName,
          success: res.status === 'COMPLETED',
          data: { path: res.target, content: res.metadata?.content },
          errorReason: res.error,
          durationMs: Date.now() - started,
          observationSummary: res.status === 'COMPLETED' ? `Read text file content from disk.` : res.error,
          verifiedState: res.status === 'COMPLETED',
        };
      }

      if (toolName === 'application.open') {
        const req: ExecutionRequest = {
          executionId: `app-${Date.now()}`,
          commandId: `cmd-${Date.now()}`,
          capability: 'APPLICATION_CONTROL',
          action: 'OPEN_APPLICATION',
          target: args.applicationName,
          requestedBy: 'user',
          workspace: 'default',
          riskLevel: 'LOW',
          policy: 'ALLOW',
          permissions: ['APPLICATION_CONTROL'],
          timestamp: new Date().toISOString(),
        };
        const res = await this.appAdapter.execute(req);
        return {
          callId: toolCall.callId,
          toolName,
          success: res.status === 'COMPLETED',
          data: { app: args.applicationName },
          errorReason: res.error,
          durationMs: Date.now() - started,
          observationSummary: res.status === 'COMPLETED' ? `Launched application ${args.applicationName}` : res.error,
          verifiedState: res.status === 'COMPLETED',
        };
      }

      if (toolName === 'application.verify_running') {
        const req: ExecutionRequest = {
          executionId: `app-${Date.now()}`,
          commandId: `cmd-${Date.now()}`,
          capability: 'APPLICATION_CONTROL',
          action: 'VERIFY_APPLICATION_RUNNING',
          target: args.applicationName,
          requestedBy: 'user',
          workspace: 'default',
          riskLevel: 'SAFE',
          policy: 'ALLOW',
          permissions: ['APPLICATION_CONTROL'],
          timestamp: new Date().toISOString(),
        };
        const res = await this.appAdapter.execute(req);
        return {
          callId: toolCall.callId,
          toolName,
          success: res.status === 'COMPLETED',
          data: { app: args.applicationName, running: res.status === 'COMPLETED' },
          durationMs: Date.now() - started,
          observationSummary: `Confirmed application ${args.applicationName} is active in OS tasklist.`,
          verifiedState: res.status === 'COMPLETED',
        };
      }

      if (toolName.startsWith('browser.')) {
        let action = 'NAVIGATE';
        if (toolName === 'browser.click') action = 'CLICK';
        else if (toolName === 'browser.type_text') action = 'TYPE_TEXT';
        else if (toolName === 'browser.read_page') action = 'READ_PAGE';
        else if (toolName === 'browser.open' || toolName === 'browser.open_tab') action = 'OPEN_TAB';

        const rawUrl = args.url || args.targetQuery || args.selector || 'https://www.google.com';
        const res = await this.browserOrchestrator.processBrowserCommand(rawUrl, action as any, rawUrl);
        return {
          callId: toolCall.callId,
          toolName,
          success: res.success,
          data: { url: res.targetUrl, extractedText: res.extractedText },
          errorReason: res.errorReason,
          durationMs: Date.now() - started,
          observationSummary: res.message,
          verifiedState: res.status === 'COMPLETED' || res.verification === 'URL_MATCHED',
        };
      }

      if (toolName.startsWith('vision.')) {
        const res = await this.visionOrchestrator.processVisionCommand('Observe Screen', 'OBSERVE_SCREEN');
        return {
          callId: toolCall.callId,
          toolName,
          success: res.success,
          data: res.observation,
          errorReason: res.errorReason,
          durationMs: Date.now() - started,
          observationSummary: res.message,
          verifiedState: res.verification === 'TARGET_VERIFIED',
        };
      }

      if (toolName.startsWith('system.')) {
        const actionMap: Record<string, string> = {
          'system.get_info': 'GET_SYSTEM_INFO',
          'system.cpu_status': 'GET_CPU_STATUS',
          'system.memory_status': 'GET_MEMORY_STATUS',
          'system.storage_status': 'GET_STORAGE_STATUS',
          'system.battery_status': 'GET_BATTERY_STATUS',
          'system.volume_get': 'GET_VOLUME',
          'system.volume_set': 'SET_VOLUME',
          'system.volume_mute': 'MUTE_VOLUME',
          'system.volume_unmute': 'UNMUTE_VOLUME',
          'system.brightness_get': 'GET_BRIGHTNESS',
          'system.brightness_set': 'SET_BRIGHTNESS',
          'system.network_status': 'GET_NETWORK_STATUS',
          'system.wifi_set': 'SET_WIFI_STATE',
          'system.bluetooth_set': 'SET_BLUETOOTH_STATE',
          'system.power_lock': 'POWER_LOCK',
          'system.power_sleep': 'POWER_SLEEP',
          'system.power_restart': 'POWER_RESTART',
          'system.power_shutdown': 'POWER_SHUTDOWN',
          'system.power_signout': 'POWER_SIGNOUT',
          'system.process_list': 'LIST_PROCESSES',
          'system.process_find': 'FIND_PROCESS',
          'system.process_terminate': 'TERMINATE_PROCESS',
          'system.screenshot_capture': 'CAPTURE_SCREENSHOT',
        };

        const mappedAction = actionMap[toolName] || 'GET_SYSTEM_INFO';
        const req: ExecutionRequest = {
          executionId: `sys-${Date.now()}`,
          commandId: `cmd-${Date.now()}`,
          capability: 'SYSTEM_CONTROL',
          action: mappedAction,
          target: args.processName || args.path || toolName,
          parameters: {
            volumeLevel: args.level,
            brightnessLevel: args.level,
            enabledState: args.enabled,
            processName: args.processName,
          },
          requestedBy: 'user',
          workspace: 'default',
          riskLevel: toolName.includes('power_') || toolName.includes('terminate') ? 'HIGH' : 'SAFE',
          policy: 'ALLOW',
          permissions: ['SYSTEM_CONTROL'],
          timestamp: new Date().toISOString(),
        };

        const res = await this.sysAdapter.execute(req);
        return {
          callId: toolCall.callId,
          toolName,
          success: res.status === 'COMPLETED',
          data: res.metadata,
          errorReason: res.error,
          durationMs: Date.now() - started,
          observationSummary: res.message,
          verifiedState: res.status === 'COMPLETED',
        };
      }

      if (toolName.startsWith('computer.')) {
        const { ComputerOrchestrator } = await import('../../computer-control/orchestrator/computerOrchestrator');
        const computer = new ComputerOrchestrator();
        const args = toolCall.arguments || {};

        let res;
        if (toolName === 'computer.observe_screen' || toolName === 'computer.screenshot') {
          const obs = await computer.observeScreen();
          return {
            callId: toolCall.callId,
            toolName,
            success: true,
            data: obs,
            durationMs: Date.now() - started,
            observationSummary: `Observed screen (${obs.width}x${obs.height}), detected ${obs.detectedElements.length} UI elements.`,
            verifiedState: true,
          };
        } else if (toolName === 'computer.click' || toolName === 'computer.double_click' || toolName === 'computer.right_click') {
          const action = toolName === 'computer.double_click' ? 'DOUBLE_CLICK' : toolName === 'computer.right_click' ? 'RIGHT_CLICK' : 'CLICK';
          res = await computer.executeMouseAction(action, args.targetQuery ? { targetType: 'BUTTON', query: args.targetQuery } : undefined, args.x, args.y);
        } else if (toolName === 'computer.type_text') {
          res = await computer.executeKeyboardAction('TYPE_TEXT', args.text);
        } else if (toolName === 'computer.press_key') {
          res = await computer.executeKeyboardAction('PRESS_KEY', undefined, args.key);
        } else if (toolName === 'computer.key_combination' || toolName === 'computer.copy' || toolName === 'computer.paste') {
          const action = toolName === 'computer.copy' ? 'COPY' : toolName === 'computer.paste' ? 'PASTE' : 'KEY_COMBINATION';
          const combo = args.keys ? (args.keys as string).split('+') : undefined;
          res = await computer.executeKeyboardAction(action, undefined, undefined, combo);
        } else {
          let winAction: any = 'FOCUS_WINDOW';
          if (toolName === 'computer.minimize_window') winAction = 'MINIMIZE_WINDOW';
          else if (toolName === 'computer.maximize_window') winAction = 'MAXIMIZE_WINDOW';
          else if (toolName === 'computer.restore_window') winAction = 'RESTORE_WINDOW';
          else if (toolName === 'computer.close_window') winAction = 'CLOSE_WINDOW';
          res = await computer.executeWindowAction(winAction, args.windowTitle || args.applicationName, args.processName);
        }


        return {
          callId: toolCall.callId,
          toolName,
          success: res.success,
          data: res.data,
          errorReason: res.errorReason,
          durationMs: Date.now() - started,
          observationSummary: res.message,
          verifiedState: res.verifiedState,
        };
      }



      return {
        callId: toolCall.callId,
        toolName,
        success: false,
        errorReason: `Tool execution fallback for ${toolName}`,
        durationMs: Date.now() - started,
        verifiedState: false,
      };
    } catch (err: any) {
      return {
        callId: toolCall.callId,
        toolName,
        success: false,
        errorReason: err?.message || 'Tool execution throw error',
        durationMs: Date.now() - started,
        verifiedState: false,
      };
    }
  }
}
