import React, { useState } from 'react';
import { Monitor, Smartphone, Laptop, Tv, Cpu, Wifi, CheckCircle2 } from 'lucide-react';
import { cn } from '@/utils/cn';
import { GlassCard } from '@/components/cards/Cards';
import { StatusBadge } from '@/components/status/StatusIndicators';
import { MOCK_DEVICES, MockDevice } from '@/mock/mockDashboardData';

export const DeviceCenterWidget: React.FC<{ className?: string }> = ({ className }) => {
  const [deviceList, setDeviceList] = useState<MockDevice[]>(MOCK_DEVICES);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const getDeviceIcon = (type: string) => {
    switch (type) {
      case 'Desktop':
        return Monitor;
      case 'Mobile':
        return Smartphone;
      case 'Laptop':
        return Laptop;
      case 'Display':
        return Tv;
      default:
        return Cpu;
    }
  };

  const handlePingDevice = (device: MockDevice) => {
    setToastMessage(`Ping sent to '${device.name}' (${device.ip}): 2.4 ms latency. Status nominal.`);
  };

  return (
    <GlassCard className={cn('p-5 space-y-4', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Monitor className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              Universal Device Mesh Center
            </h3>
            <p className="text-xs text-slate-400">Cross-platform device orchestration & edge nodes</p>
          </div>
        </div>
        <StatusBadge label="5 MESH NODES" variant="info" />
      </div>

      {/* Device Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {deviceList.map((dev) => {
          const Icon = getDeviceIcon(dev.type);
          return (
            <div
              key={dev.id}
              className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 hover:border-slate-700 transition-all space-y-2.5"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2.5">
                  <div className="p-2 rounded-xl bg-slate-800 text-slate-200 border border-slate-700">
                    <Icon className="w-4 h-4 text-cyan-400" />
                  </div>
                  <div>
                    <div className="text-xs font-bold text-slate-100">{dev.name}</div>
                    <div className="text-[10px] font-mono text-slate-400">{dev.os}</div>
                  </div>
                </div>
                <StatusBadge
                  label={dev.status}
                  variant={
                    dev.status === 'online'
                      ? 'success'
                      : dev.status === 'connected'
                      ? 'cyan'
                      : dev.status === 'attention'
                      ? 'warning'
                      : 'danger'
                  }
                />
              </div>

              <div className="text-[11px] font-mono text-slate-300 space-y-1 bg-slate-950/60 p-2 rounded-xl border border-slate-800/60">
                <div className="truncate">IP: <span className="text-cyan-300">{dev.ip}</span></div>
                <div className="truncate text-slate-400">{dev.specs}</div>
                {dev.batteryPercent !== undefined && (
                  <div className="flex justify-between text-slate-400">
                    <span>Battery: <strong className="text-emerald-400">{dev.batteryPercent}%</strong></span>
                    {dev.signalStrength && <span>{dev.signalStrength}</span>}
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between pt-1">
                <span className="text-[10px] font-mono text-slate-500">{dev.lastActive}</span>
                <button
                  onClick={() => handlePingDevice(dev)}
                  className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-cyan-300 text-[11px] font-mono transition-all cursor-pointer flex items-center space-x-1"
                >
                  <Wifi className="w-3 h-3" />
                  <span>Ping</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Simulated Device Toast */}
      {toastMessage && (
        <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-200 text-xs font-mono flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0" />
            <span>{toastMessage}</span>
          </div>
          <button onClick={() => setToastMessage(null)} className="text-slate-400 hover:text-slate-200 text-xs">
            Dismiss
          </button>
        </div>
      )}
    </GlassCard>
  );
};

export default DeviceCenterWidget;
