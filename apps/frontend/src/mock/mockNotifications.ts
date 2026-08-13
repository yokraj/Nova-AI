import { NotificationItem } from '@/types';

export const MOCK_NOTIFICATIONS: NotificationItem[] = [
  {
    id: 'notif-1',
    title: 'Platform System Hardened',
    message: 'Phase M3.6.7 validation completed with 100% test pass rate.',
    type: 'success',
    timestamp: '10 mins ago',
    read: false,
  },
  {
    id: 'notif-2',
    title: 'Inference Gateway Online',
    message: 'Ollama local engine connected on port 11434.',
    type: 'info',
    timestamp: '1 hour ago',
    read: true,
  },
];
