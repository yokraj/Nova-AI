import React, { useState } from 'react';
import {
  Bell,
  CheckCheck,
  Trash2,
  Info,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  X,
  Filter,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import { NotificationItem } from '@/types';
import { MOCK_NOTIFICATIONS } from '@/mock/mockNotifications';

interface NotificationsWidgetProps {
  className?: string;
  initialNotifications?: NotificationItem[];
  onMarkRead?: (id: string) => void;
  onDeleteNotification?: (id: string) => void;
}

export const NotificationsWidget: React.FC<NotificationsWidgetProps> = ({
  className,
  initialNotifications,
  onMarkRead,
  onDeleteNotification,
}) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>(
    initialNotifications || [
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
      {
        id: 'notif-5',
        title: 'High VRAM Threshold Warning',
        message: 'VRAM usage spiked to 82% during 32k context batching.',
        type: 'warning',
        timestamp: '1 hour ago',
        read: true,
      },
    ]
  );

  React.useEffect(() => {
    if (initialNotifications) {
      setNotifications(initialNotifications);
    }
  }, [initialNotifications]);

  const [severityFilter, setSeverityFilter] = useState<'all' | 'info' | 'success' | 'warning' | 'error'>('all');

  const markAllRead = () => {
    notifications.forEach((n) => onMarkRead?.(n.id));
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const markOneRead = (id: string) => {
    if (onMarkRead) onMarkRead(id);
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const dismissNotification = (id: string) => {
    if (onDeleteNotification) onDeleteNotification(id);
    setNotifications((prev) => prev.filter((n) => n.id !== id));
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

  const filteredNotifications = notifications.filter((n) => {
    if (severityFilter === 'all') return true;
    return n.type === severityFilter;
  });

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <div
      className={cn(
        'glass-panel p-5 rounded-2xl sm:rounded-3xl border border-slate-800/80 bg-slate-950/70 backdrop-blur-xl space-y-4 shadow-xl select-none',
        className
      )}
    >
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-slate-800 pb-3 gap-2">
        <div className="flex items-center space-x-2.5">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 relative shrink-0">
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
            )}
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-100 uppercase tracking-wider font-sans">
              System Notifications & Alerts
            </h3>
            <p className="text-xs text-slate-400 font-mono">
              {unreadCount} unread system notifications
            </p>
          </div>
        </div>

        {/* Global Notification Actions */}
        <div className="flex items-center space-x-2">
          {unreadCount > 0 && (
            <button
              onClick={markAllRead}
              className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-300 text-xs font-mono transition-all cursor-pointer flex items-center space-x-1"
              title="Mark All Read"
            >
              <CheckCheck className="w-3.5 h-3.5" />
              <span>Mark Read</span>
            </button>
          )}

          {notifications.length > 0 && (
            <button
              onClick={clearAll}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-rose-400 text-xs transition-all cursor-pointer"
              title="Clear All Notifications"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Severity Filter Tabs */}
      <div className="flex items-center space-x-1 bg-slate-900/80 p-1 rounded-xl border border-slate-800 text-[11px] font-mono overflow-x-auto">
        <Filter className="w-3 h-3 text-slate-500 ml-1 mr-0.5 shrink-0" />
        {(['all', 'info', 'success', 'warning', 'error'] as const).map((sev) => (
          <button
            key={sev}
            onClick={() => setSeverityFilter(sev)}
            className={cn(
              'px-2.5 py-1 rounded-lg uppercase tracking-wider transition-all cursor-pointer whitespace-nowrap',
              severityFilter === sev
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                : 'text-slate-400 hover:text-slate-200'
            )}
          >
            {sev}
          </button>
        ))}
      </div>

      {/* Notifications List Feed */}
      <div className="space-y-2.5 max-h-[380px] overflow-y-auto pr-1">
        {filteredNotifications.length === 0 ? (
          <div className="py-8 text-center text-xs font-mono text-slate-500 rounded-2xl bg-slate-900/40 border border-slate-800/80">
            No system notifications for filter "{severityFilter}".
          </div>
        ) : (
          filteredNotifications.map((notif) => {
            const Icon = getTypeIcon(notif.type);
            return (
              <div
                key={notif.id}
                className={cn(
                  'p-3.5 rounded-2xl border transition-all space-y-1 relative group',
                  !notif.read
                    ? 'bg-slate-900 border-cyan-500/40 shadow-[0_0_10px_rgba(0,240,255,0.1)]'
                    : 'bg-slate-900/50 border-slate-800/80 opacity-80 hover:opacity-100'
                )}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 min-w-0">
                    <Icon
                      className={cn(
                        'w-4 h-4 shrink-0',
                        notif.type === 'success'
                          ? 'text-emerald-400'
                          : notif.type === 'warning'
                          ? 'text-amber-400'
                          : notif.type === 'error'
                          ? 'text-rose-400'
                          : 'text-cyan-400'
                      )}
                    />
                    <h4 className="text-xs font-bold text-slate-100 truncate">{notif.title}</h4>
                    {!notif.read && (
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0" />
                    )}
                  </div>

                  <div className="flex items-center space-x-2 shrink-0">
                    <span className="text-[10px] font-mono text-slate-500">{notif.timestamp}</span>
                    <button
                      onClick={() => dismissNotification(notif.id)}
                      className="text-slate-500 hover:text-slate-300 opacity-0 group-hover:opacity-100 transition-opacity p-0.5"
                      title="Dismiss notification"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>

                <p className="text-xs text-slate-300 font-sans leading-relaxed pl-6">{notif.message}</p>

                {!notif.read && (
                  <div className="flex justify-end pt-1">
                    <button
                      onClick={() => markOneRead(notif.id)}
                      className="text-[10px] font-mono text-cyan-400 hover:text-cyan-200 cursor-pointer"
                    >
                      Mark as Read
                    </button>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default NotificationsWidget;
