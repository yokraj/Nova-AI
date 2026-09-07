export interface LocalNotification {
  id: string;
  title: string;
  body: string;
  type: 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR' | 'APPROVAL_REQUIRED';
  timestamp: string;
  read: boolean;
}

export class LocalNotificationProvider {
  private notifications: LocalNotification[] = [];

  notify(title: string, body: string, type: LocalNotification['type'] = 'INFO'): LocalNotification {
    const notification: LocalNotification = {
      id: `notif-${Date.now()}-${Math.random().toString(36).substr(2, 4)}`,
      title,
      body,
      type,
      timestamp: new Date().toISOString(),
      read: false,
    };

    this.notifications.unshift(notification);

    // Browser Notification API if supported and granted
    if (typeof window !== 'undefined' && 'Notification' in window && window.Notification.permission === 'granted') {
      try {
        new window.Notification(title, { body });
      } catch {
        // Fallback
      }
    }

    return notification;
  }

  getNotifications(): LocalNotification[] {
    return [...this.notifications];
  }

  markAllRead(): void {
    this.notifications.forEach((n) => (n.read = true));
  }

  clear(): void {
    this.notifications = [];
  }
}
