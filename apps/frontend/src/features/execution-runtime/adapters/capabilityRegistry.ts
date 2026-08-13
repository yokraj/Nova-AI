import { CapabilityAdapter } from '../types/capability';
import { ExecutionRequest } from '../types/executionRequest';
import { WindowsApplicationAdapter } from './windowsApplicationAdapter';
import { WindowsFileSystemAdapter } from '../../file-system/adapters/windowsFileSystemAdapter';

export class CapabilityRegistry {
  private adapters: CapabilityAdapter[] = [
    new WindowsApplicationAdapter(),
    new WindowsFileSystemAdapter(),
  ];

  registerAdapter(adapter: CapabilityAdapter): void {
    this.adapters.push(adapter);
  }

  findAdapter(request: ExecutionRequest): CapabilityAdapter | null {
    return this.adapters.find((adapter) => adapter.canHandle(request)) || null;
  }
}
