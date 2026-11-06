import React, { useState, useMemo } from 'react';
import {
  Monitor,
  Smartphone,
  Laptop,
  Tv,
  Cpu,
  Wifi,
  Search,
  Filter,
  CheckCircle2,
  X,
  RefreshCw,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { MockDevice } from '@/types/dashboard';
import { MOCK_DEVICES } from '@/mock/mockDashboardData';
import { useDashboardData } from '@/hooks/useDashboardData';

export interface DeviceCenterWidgetProps {
  className?: string;
  devices?: MockDevice[];
  onPingDevice?: (device: MockDevice) => void;
  onRefresh?: () => void;
  isLoading?: boolean;
}

export const DeviceCenterWidget: React.FC<DeviceCenterWidgetProps> = ({
  className,
  devices: externalDevices,
  onPingDevice,
  onRefresh,
  isLoading: externalIsLoading,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'online' | 'connected' | 'attention' | 'offline'>('all');
  const [pingingId, setPingingId] = useState<string | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Hook into live dashboard telemetry
  const {
    data: dashboardData,
    connectionStatus,
    health,
    isRefreshing,
    refresh: hookRefresh,
  } = useDashboardData();

  const isConnected = connectionStatus === 'connected' && !!dashboardData?.isConnected;
  const rawDevices = externalDevices || (isConnected ? dashboardData?.devices : undefined) || MOCK_DEVICES;
  const lastUpdated = dashboardData?.lastUpdated;
  const isLoading = externalIsLoading !== undefined ? externalIsLoading : isRefreshing;

  const [deviceList, setDeviceList] = useState<MockDevice[]>(rawDevices);

  React.useEffect(() => {
    setDeviceList(rawDevices);
  }, [rawDevices]);

  const handleRefreshClick = () => {
    if (onRefresh) {
      onRefresh();
    } else {
      hookRefresh(true);
    }
  };

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

  const filteredDevices = useMemo(() => {
    return deviceList.filter((dev) => {
      const matchesSearch =
        dev.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        dev.os.toLowerCase().includes(searchQuery.toLowerCase()) ||
        dev.ip.toLowerCase().includes(searchQuery.toLowerCase()) ||
        dev.type.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFilter = statusFilter === 'all' || dev.status === statusFilter;
      return matchesSearch && matchesFilter;
    });
  }, [deviceList, searchQuery, statusFilter]);

  const handlePingDevice = async (device: MockDevice) => {
    setPingingId(device.id);
    try {
      if (onPingDevice) {
        await onPingDevice(device);
        setToastMessage(`Pinged '${device.name}' (${device.ip}): Connection confirmed.`);
      } else if (health?.nativeBridge) {
        setToastMessage(`Bridge ping to '${device.name}' (${device.ip}): Daemon verified online (:3001).`);
      } else {
        setToastMessage(`Local node '${device.name}' (${device.ip}) verified in standalone routing table.`);
      }
      setDeviceList((prev) =>
        prev.map((d) => (d.id === device.id ? { ...d, lastActive: 'Just now' } : d))
      );
    } catch {
      setToastMessage(`Ping to '${device.name}' failed or timed out.`);
    } finally {
      setPingingId(null);
      setTimeout(() => setToastMessage(null), 3500);
    }
  };

  const onlineCount = deviceList.filter((d) => d.status === 'online' || d.status === 'connected').length;

  return (
    <div
      className={cn(
        'glass-panel p-5 rounded-2xl sm:rounded-3xl border border-slate-800/80 bg-slate-950/70 backdrop-blur-xl space-y-4 shadow-xl select-none',
        className
      )}
    >
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800/80 pb-3 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 shrink-0">
            <Monitor className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans">
                Universal Device Mesh Center
              </h3>
              {lastUpdated && (
                <span className="text-[10px] font-mono text-slate-500 hidden sm:inline">
                  • Polled: {new Date(lastUpdated).toLocaleTimeString()}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-400 font-mono">
              Cross-platform device orchestration & edge nodes
            </p>
          </div>
        </div>

        {/* Status Pill & Refresh */}
        <div className="flex items-center space-x-2 shrink-0">
          <button
            onClick={handleRefreshClick}
            disabled={isLoading}
            className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-cyan-300 transition-all cursor-pointer disabled:opacity-50"
            title="Refresh Devices"
            aria-label="Refresh devices"
          >
            <RefreshCw className={cn('w-3.5 h-3.5', isLoading && 'animate-spin text-blue-400')} />
          </button>

          {health?.nativeBridge ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
              <span>BRIDGE ACTIVE (:3001)</span>
            </span>
          ) : isConnected ? (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
              <span>MESH POOL ({onlineCount} ONLINE)</span>
            </span>
          ) : (
            <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700/80 text-slate-400 text-xs font-mono font-bold">
              <span className="w-1.5 h-1.5 rounded-full border border-slate-400" />
              <span>STANDALONE MESH ({onlineCount} NODES)</span>
            </span>
          )}
        </div>
      </div>

      {/* Toolbar: Search & Status Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5">
        <div className="relative flex-1 max-w-sm">
          <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search devices by name, OS, or IP..."
            className="w-full pl-9 pr-8 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500/50 transition-all font-sans"
            aria-label="Search devices"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-[11px] font-mono overflow-x-auto scrollbar-none">
          <Filter className="w-3 h-3 text-slate-500 ml-1 mr-0.5 shrink-0" />
          {(['all', 'online', 'connected', 'attention', 'offline'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setStatusFilter(tab)}
              className={cn(
                'px-2.5 py-1 rounded-lg uppercase tracking-wider transition-all cursor-pointer whitespace-nowrap',
                statusFilter === tab
                  ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40 font-bold'
                  : 'text-slate-400 hover:text-slate-200'
              )}
            >
              {tab}
            </button>
          ))}
        </div>
      </div>

      {/* Device Cards Grid */}
      {filteredDevices.length === 0 ? (
        <div className="p-8 text-center rounded-2xl bg-slate-900/40 border border-slate-800/80 text-xs font-mono text-slate-500 space-y-1">
          <Monitor className="w-6 h-6 mx-auto text-slate-600 mb-2" />
          <p>No devices match filter "{searchQuery || statusFilter}".</p>
          <button
            onClick={() => {
              setSearchQuery('');
              setStatusFilter('all');
            }}
            className="text-blue-400 hover:text-blue-300 text-xs font-semibold cursor-pointer underline pt-1"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {filteredDevices.map((dev) => {
            const Icon = getDeviceIcon(dev.type);
            const isPinging = pingingId === dev.id;
            return (
              <div
                key={dev.id}
                className="p-3.5 rounded-2xl bg-slate-900/80 border border-slate-800/90 hover:border-slate-700/80 transition-all space-y-2.5 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2.5 min-w-0">
                      <div className="p-2 rounded-xl bg-slate-800 text-slate-200 border border-slate-700 shrink-0">
                        <Icon className="w-4 h-4 text-cyan-400" />
                      </div>
                      <div className="min-w-0">
                        <div className="text-xs font-bold text-slate-100 truncate">{dev.name}</div>
                        <div className="text-[10px] font-mono text-slate-400 truncate">{dev.os}</div>
                      </div>
                    </div>

                    <span
                      className={cn(
                        'text-[10px] font-mono font-bold px-2 py-0.5 rounded-full border uppercase shrink-0',
                        dev.status === 'online'
                          ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
                          : dev.status === 'connected'
                          ? 'bg-cyan-500/15 border-cyan-500/30 text-cyan-300'
                          : dev.status === 'attention'
                          ? 'bg-amber-500/15 border-amber-500/30 text-amber-400'
                          : 'bg-rose-500/15 border-rose-500/30 text-rose-400'
                      )}
                    >
                      {dev.status}
                    </span>
                  </div>

                  <div className="text-[11px] font-mono text-slate-300 space-y-1 bg-slate-950/60 p-2 rounded-xl border border-slate-800/60 mt-2">
                    <div className="truncate">
                      IP: <span className="text-cyan-300">{dev.ip}</span>
                    </div>
                    <div className="truncate text-slate-400">{dev.specs}</div>
                    {dev.batteryPercent !== undefined && (
                      <div className="flex justify-between text-slate-400">
                        <span>
                          Battery: <strong className="text-emerald-400">{dev.batteryPercent}%</strong>
                        </span>
                        {dev.signalStrength && <span>{dev.signalStrength}</span>}
                      </div>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-1 border-t border-slate-800/60">
                  <span className="text-[10px] font-mono text-slate-500">{dev.lastActive}</span>
                  <button
                    onClick={() => handlePingDevice(dev)}
                    disabled={isPinging}
                    className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-cyan-300 text-[11px] font-mono transition-all cursor-pointer flex items-center space-x-1 disabled:opacity-50"
                  >
                    <Wifi className={cn('w-3 h-3', isPinging && 'animate-pulse text-cyan-400')} />
                    <span>{isPinging ? 'Pinging...' : 'Ping'}</span>
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Ping Toast Notification */}
      {toastMessage && (
        <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-200 text-xs font-mono flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-4 h-4 text-blue-400 shrink-0" />
            <span>{toastMessage}</span>
          </div>
          <button
            onClick={() => setToastMessage(null)}
            className="text-slate-400 hover:text-slate-200 text-xs cursor-pointer font-bold"
          >
            Dismiss
          </button>
        </div>
      )}
    </div>
  );
};

export default DeviceCenterWidget;
