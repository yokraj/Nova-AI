import React, { useState } from 'react';
import { Bell, CheckCheck, Trash2, Info, CheckCircle2, AlertTriangle, AlertCircle } from 'lucide-react';
import { cn } from '@/utils/cn';
import { GlassCard } from '@/components/cards/Cards';
import { StatusBadge } from '@/components/status/StatusIndicators';
import { MOCK_NOTIFICATIONS } from '@/mock/mockNotifications';
import { NotificationItem } from '@/types';

export const NotificationsWidget: React.FC<{ className?: string }> = ({ className }) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([
    ...MOCK_NOTIFICATIONS,
    {
      id: 'notif-3',
      title: 'Automation Workflow Executed',
      message: 'Morning Standup routine completed 5 subtasks in 1.4s.',
      type: 'success',
      timestamp: '15 mins ago',
      read: false,
    },
    {
      id: 'notif-4',
      title: 'Security Vulnerability Scan',
      message: 'Static analysis clean: 0 critical flaws across 73 packages.',
      type: 'info',
      timestamp: '35 mins ago',
      read: false,
    },
  ]);

  const markAllRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'success':
        return CheckCircle2;
      case 'warning':
        return AlertTriangle;
      case 'error':
        return AlertCircle;
      default:
        return Info;
    }
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <GlassCard className={cn('p-5 space-y-4', className)}>
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 relative">
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
            )}
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider">
              System Notifications & Alerts
            </h3>
            <p className="text-xs text-slate-400">{unreadCount} unread system notifications</p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={markAllRead}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-300 text-xs font-mono transition-all cursor-pointer flex items-center space-x-1"
            title="Mark All Read"
          >
            <CheckCheck className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Mark Read</span>
          </button>
          <button
            onClick={clearAll}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-rose-400 text-xs transition-all cursor-pointer"
            title="Clear All"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Notifications List Feed */}
      <div className="space-y-2.5">
        {notifications.length === 0 ? (
          <div className="py-8 text-center text-xs font-mono text-slate-500">
            No active system notifications
          </div>
        ) : (
          notifications.map((notif) => {
            const Icon = getTypeIcon(notif.type);
            return (
              <div
                key={notif.id}
                className={cn(
                  'p-3.5 rounded-2xl border transition-all space-y-1',
                  !notif.read
                    ? 'bg-slate-900 border-cyan-500/40 shadow-[0_0_10px_rgba(0,240,255,0.1)]'
                    : 'bg-slate-900/50 border-slate-800/80 opacity-80'
                )}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Icon className={cn('w-4 h-4', notif.type === 'success' ? 'text-emerald-400' : notif.type === 'warning' ? 'text-amber-400' : 'text-cyan-400')} />
                    <h4 className="text-xs font-bold text-slate-100">{notif.title}</h4>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-mono text-slate-500">{notif.timestamp}</span>
                    <StatusBadge
                      label={notif.type}
                      variant={notif.type === 'success' ? 'success' : notif.type === 'warning' ? 'warning' : 'info'}
                    />
                  </div>
                </div>
                <p className="text-xs text-slate-300 font-sans leading-relaxed pl-6">{notif.message}</p>
              </div>
            );
          })
        )}
      </div>
    </GlassCard>
  );
};

export default NotificationsWidget;
