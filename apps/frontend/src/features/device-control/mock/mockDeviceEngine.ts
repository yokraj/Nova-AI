import { DeviceItem, DeviceProvider } from '../types/device';
import { DeviceActionRequest, ActionRiskLevel, CommandPolicy, ActionApprovalProvider } from '../types/deviceAction';
import { MOCK_DEVICES, MOCK_ACTION_HISTORY } from './mockDeviceData';

export class MockDeviceEngine implements DeviceProvider, ActionApprovalProvider {
  private devices: DeviceItem[] = [...MOCK_DEVICES];
  private actions: DeviceActionRequest[] = [...MOCK_ACTION_HISTORY];

  listDevices(): DeviceItem[] {
    return this.devices;
  }

  getDeviceById(id: string): DeviceItem | undefined {
    return this.devices.find((d) => d.id === id);
  }

  calculateRisk(commandText: string, capability: string): ActionRiskLevel {
    const lower = commandText.toLowerCase();
    if (lower.includes('delete') || lower.includes('restart') || lower.includes('shutdown')) return 'HIGH';
    if (lower.includes('send') || lower.includes('move') || lower.includes('call')) return 'MEDIUM';
    if (lower.includes('open') || lower.includes('turn on') || lower.includes('find')) return 'SAFE';
    return 'LOW';
  }

  checkPolicy(riskLevel: ActionRiskLevel): CommandPolicy {
    if (riskLevel === 'CRITICAL' || riskLevel === 'HIGH') return 'ALLOW_WITH_APPROVAL';
    return 'ALLOW';
  }

  previewAction(commandText: string, targetDeviceId: string): DeviceActionRequest {
    const device = this.getDeviceById(targetDeviceId) || this.devices[0];
    const riskLevel = this.calculateRisk(commandText, 'APPLICATION_CONTROL');
    const policy = this.checkPolicy(riskLevel);

    return {
      id: `act-${Date.now()}`,
      commandText,
      targetDeviceId: device.id,
      targetDeviceName: device.name,
      actionType: 'Control Action',
      capabilityRequired: 'APPLICATION_CONTROL',
      riskLevel,
      policy,
      scope: 'Local Environment',
      requiresApproval: policy === 'ALLOW_WITH_APPROVAL',
      status: 'PREVIEW',
      timestamp: new Date().toLocaleTimeString(),
    };
  }

  executeMockAction(actionId: string): DeviceActionRequest {
    const act = this.actions.find((a) => a.id === actionId) || this.previewAction('Command Execution', 'dev-pc-01');
    act.status = 'COMPLETED';
    act.durationSeconds = 0.8;
    act.resultMessage = `Command "${act.commandText}" completed cleanly on target device "${act.targetDeviceName}".`;
    this.actions.unshift(act);
    return act;
  }

  async requestApproval(actionId: string): Promise<boolean> {
    return true;
  }

  getActionHistory(): DeviceActionRequest[] {
    return this.actions;
  }
}
