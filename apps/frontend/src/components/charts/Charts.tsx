import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip as RechartsTooltip,
} from 'recharts';
import { cn } from '@/utils/cn';

export interface ChartDataPoint {
  label: string;
  value: number;
}

export const MiniLineChart: React.FC<{ data: ChartDataPoint[]; height?: number; color?: string; className?: string }> = ({
  data,
  height = 80,
  color = '#00f0ff',
  className,
}) => (
  <div className={cn('w-full', className)} style={{ height }}>
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  </div>
);

export const MiniAreaChart: React.FC<{ data: ChartDataPoint[]; height?: number; color?: string; className?: string }> = ({
  data,
  height = 100,
  color = '#00f0ff',
  className,
}) => (
  <div className={cn('w-full', className)} style={{ height }}>
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart data={data}>
        <defs>
          <linearGradient id="cyanGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor={color} stopOpacity={0.4} />
            <stop offset="95%" stopColor={color} stopOpacity={0.0} />
          </linearGradient>
        </defs>
        <XAxis dataKey="label" stroke="#64748b" fontSize={10} tickLine={false} />
        <YAxis hide />
        <RechartsTooltip
          contentStyle={{ backgroundColor: '#0f172a', borderColor: '#00f0ff', borderRadius: '8px', fontSize: '11px' }}
        />
        <Area type="monotone" dataKey="value" stroke={color} fillOpacity={1} fill="url(#cyanGradient)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  </div>
);

export const PlaceholderChart: React.FC<{ title?: string; height?: number; className?: string }> = ({ title = 'Telemetry Distribution', height = 140, className }) => {
  const sampleData: ChartDataPoint[] = [
    { label: '10:00', value: 12 },
    { label: '11:00', value: 25 },
    { label: '12:00', value: 18 },
    { label: '13:00', value: 42 },
    { label: '14:00', value: 35 },
  ];

  return (
    <div className={cn('glass-panel p-4 rounded-2xl space-y-2', className)}>
      <div className="text-xs font-bold text-slate-300 uppercase tracking-wider">{title}</div>
      <MiniAreaChart data={sampleData} height={height} />
    </div>
  );
};
