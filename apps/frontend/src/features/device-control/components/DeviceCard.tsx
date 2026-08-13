import React from 'react';
import { Laptop, Smartphone, Lightbulb, Tv, ChevronRight } from 'lucide-react';
import { cn } from '@/utils/cn';
import { DeviceItem } from '../types/device';
import DeviceStatusBadge from './DeviceStatusBadge';

interface DeviceCardProps {
  device: DeviceItem;
  onSelect: () => void;
  className?: string;
}

export const DeviceCard: React.FC<DeviceCardProps> = ({
  device,
  onSelect,
  className,
}) => {
  const getDeviceIcon = () => {
    switch (device.type) {
      case 'DESKTOP':
      case 'LAPTOP':
        return <Laptop className="w-5 h-5 text-cyan-400" />;
      case 'PHONE':
      case 'TABLET':
        return <Smartphone className="w-5 h-5 text-purple-400" />;
      case 'SMART_LIGHT':
        return <Lightbulb className="w-5 h-5 text-amber-400" />;
      case 'SMART_TV':
        return <Tv className="w-5 h-5 text-blue-400" />;
      default:
        return <Laptop className="w-5 h-5 text-cyan-400" />;
    }
  };

  const isOnline = device.status === 'ONLINE';

  return (
    <div
      onClick={onSelect}
      className={cn(
        'p-4.5 rounded-3xl bg-slate-900/80 border transition-all cursor-pointer space-y-3 group shadow-xl relative',
        isOnline
          ? 'border-cyan-500/40 bg-slate-900 shadow-[0_0_15px_rgba(0,240,255,0.1)]'
          : 'border-slate-800/90 hover:border-slate-700 opacity-80'
      )}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2.5">
          <div className="p-2.5 rounded-2xl bg-slate-950 border border-slate-800">
            {getDeviceIcon()}
          </div>
          <div>
            <h4 className="text-sm font-bold font-sans text-slate-100 group-hover:text-cyan-300 transition-colors">
              {device.name}
            </h4>
            <span className="text-[10px] font-mono text-slate-400">{device.platform}</span>
          </div>
        </div>

        <DeviceStatusBadge status={device.status} />
      </div>

      <div className="grid grid-cols-2 gap-2 text-[11px] font-mono pt-1">
        <div className="p-2 rounded-xl bg-slate-950/80 border border-slate-800/80 text-slate-300">
          <span className="text-slate-500 block text-[10px]">Connection</span>
          <span className="font-bold text-cyan-300">{device.connection}</span>
        </div>

        <div className="p-2 rounded-xl bg-slate-950/80 border border-slate-800/80 text-slate-300">
          <span className="text-slate-500 block text-[10px]">Trust State</span>
          <span className="font-bold text-purple-300">{device.trustState}</span>
        </div>
      </div>

      <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 pt-2 border-t border-slate-800">
        <span className="text-slate-500">Location: {device.location || 'Local Net'}</span>
        <div className="flex items-center text-cyan-400 font-bold group-hover:translate-x-0.5 transition-transform">
          <span>Control Panel</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </div>
      </div>
    </div>
  );
};

export default DeviceCard;
