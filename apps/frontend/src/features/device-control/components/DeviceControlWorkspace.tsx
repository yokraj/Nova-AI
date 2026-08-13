import React, { useState } from 'react';
import { Laptop, Terminal } from 'lucide-react';
import { MOCK_DEVICES } from '../mock/mockDeviceData';
import { MockDeviceEngine } from '../mock/mockDeviceEngine';
import { DeviceItem } from '../types/device';
import { DeviceActionRequest } from '../types/deviceAction';
import DeviceCard from './DeviceCard';
import DeviceCommandPreview from './DeviceCommandPreview';
import ActionPermissionDialog from './ActionPermissionDialog';
import ApplicationControlPanel from './ApplicationControlPanel';
import FileControlPanel from './FileControlPanel';
import PhoneControlPanel from './PhoneControlPanel';
import SmartDevicePanel from './SmartDevicePanel';
import SystemControlPanel from './SystemControlPanel';

export const DeviceControlWorkspace: React.FC = () => {
  const [engine] = useState(new MockDeviceEngine());
  const [devices] = useState<DeviceItem[]>(MOCK_DEVICES);
  const [commandInput, setCommandInput] = useState('');
  const [activePreview, setActivePreview] = useState<DeviceActionRequest | null>(null);
  const [activeApproval, setActiveApproval] = useState<DeviceActionRequest | null>(null);
  const [selectedDevice, setSelectedDevice] = useState<DeviceItem | null>(null);

  const handlePreviewCommand = (cmd: string) => {
    const prev = engine.previewAction(cmd, selectedDevice?.id || 'dev-pc-01');
    setActivePreview(prev);
  };

  const handleExecuteAction = () => {
    if (!activePreview) return;
    if (activePreview.requiresApproval) {
      setActiveApproval(activePreview);
    } else {
      engine.executeMockAction(activePreview.id);
      setActivePreview(null);
    }
  };

  const handleApproveAction = () => {
    if (activeApproval) {
      engine.executeMockAction(activeApproval.id);
      setActiveApproval(null);
      setActivePreview(null);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header Stat Panel */}
      <div className="p-6 rounded-3xl bg-slate-900/90 border border-cyan-500/30 flex flex-col md:flex-row items-center justify-between gap-4 shadow-2xl">
        <div className="flex items-center space-x-3">
          <div className="p-3 rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Laptop className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-100">Universal Device & System Control</h1>
            <p className="text-xs text-slate-400 font-mono">
              Secure local device mesh & OS capability orchestration
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 font-mono text-xs">
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-emerald-400 font-bold">3</span> Online
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-300">
            <span className="text-slate-500 font-bold">1</span> Offline
          </div>
        </div>
      </div>

      {/* Universal Command Input Bar */}
      <div className="p-4 rounded-3xl bg-slate-950 border border-cyan-500/40 space-y-3 shadow-2xl">
        <div className="text-xs font-mono font-bold text-cyan-300 uppercase tracking-wider flex items-center space-x-2">
          <Terminal className="w-4 h-4 text-cyan-400" />
          <span>Natural-Language System Command</span>
        </div>
        <div className="flex items-center space-x-2">
          <input
            type="text"
            value={commandInput}
            onChange={(e) => setCommandInput(e.target.value)}
            placeholder="Type a command (e.g. 'Open VS Code', 'Turn on bedroom light', 'Take a screenshot')..."
            className="w-full bg-slate-900 border border-slate-800 rounded-2xl py-2.5 px-4 text-xs text-slate-100 placeholder-slate-500 font-sans focus:outline-none focus:border-cyan-500/50"
            onKeyDown={(e) => {
              if (e.key === 'Enter' && commandInput) {
                handlePreviewCommand(commandInput);
              }
            }}
          />
          <button
            onClick={() => commandInput && handlePreviewCommand(commandInput)}
            className="px-4 py-2.5 rounded-2xl bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 font-bold font-mono text-xs transition-all cursor-pointer shrink-0"
          >
            Preview Command
          </button>
        </div>
      </div>

      {/* Active Command Pipeline Preview */}
      {activePreview && (
        <DeviceCommandPreview
          action={activePreview}
          onExecute={handleExecuteAction}
        />
      )}

      {/* Connected Devices Roster */}
      <div className="space-y-3">
        <div className="text-xs font-mono font-bold text-slate-400 uppercase tracking-wider">
          Connected Device Mesh ({devices.length})
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {devices.map((device) => (
            <DeviceCard
              key={device.id}
              device={device}
              onSelect={() => setSelectedDevice(device)}
            />
          ))}
        </div>
      </div>

      {/* Domain Control Panels */}
      <div className="space-y-6">
        <ApplicationControlPanel onExecuteCommand={handlePreviewCommand} />
        <SystemControlPanel onExecuteCommand={handlePreviewCommand} />
        <FileControlPanel onExecuteCommand={handlePreviewCommand} />
        <PhoneControlPanel onExecuteCommand={handlePreviewCommand} />
        <SmartDevicePanel onExecuteCommand={handlePreviewCommand} />
      </div>

      {/* Security Approval Gate Modal */}
      <ActionPermissionDialog
        action={activeApproval}
        onApprove={handleApproveAction}
        onReject={() => setActiveApproval(null)}
      />
    </div>
  );
};

export default DeviceControlWorkspace;
