import { ScheduledTask, TaskSchedule } from '../types/scheduledTask';
import { CronParser } from './cronParser';

export class LocalScheduler {
  calculateNextRun(task: ScheduledTask, referenceDate: Date = new Date()): string | undefined {
    if (!task.enabled || !task.schedule || task.status === 'CANCELLED' || task.status === 'EXPIRED') {
      return undefined;
    }

    const sched = task.schedule;
    const now = referenceDate;

    if (sched.type === 'ONE_TIME') {
      if (sched.runAtTimestamp) {
        const runDate = new Date(sched.runAtTimestamp);
        return runDate > now ? runDate.toISOString() : undefined;
      }
      return undefined;
    }

    if (sched.type === 'INTERVAL') {
      const mins = sched.intervalMinutes || 30;
      return new Date(now.getTime() + mins * 60 * 1000).toISOString();
    }

    if (sched.type === 'CRON' && sched.cronExpression) {
      return CronParser.parseNextRun(sched.cronExpression, now).toISOString();
    }

    if (sched.type === 'DAILY') {
      const next = new Date(now);
      const [hh, mm] = (sched.timeOfDay || '09:00').split(':').map((v) => parseInt(v, 10));
      next.setHours(hh || 9, mm || 0, 0, 0);
      if (next <= now) {
        next.setDate(next.getDate() + 1);
      }
      return next.toISOString();
    }

    if (sched.type === 'WEEKLY') {
      const next = new Date(now);
      const targetDay = sched.dayOfWeek !== undefined ? sched.dayOfWeek : 1; // Default Monday
      const [hh, mm] = (sched.timeOfDay || '09:00').split(':').map((v) => parseInt(v, 10));
      next.setHours(hh || 9, mm || 0, 0, 0);

      while (next.getDay() !== targetDay || next <= now) {
        next.setDate(next.getDate() + 1);
      }
      return next.toISOString();
    }

    if (sched.type === 'MONTHLY') {
      const next = new Date(now);
      const targetDay = sched.dayOfMonth || 1;
      const [hh, mm] = (sched.timeOfDay || '09:00').split(':').map((v) => parseInt(v, 10));
      next.setDate(targetDay);
      next.setHours(hh || 9, mm || 0, 0, 0);
      if (next <= now) {
        next.setMonth(next.getMonth() + 1);
      }
      return next.toISOString();
    }

    return undefined;
  }

  isTaskDue(task: ScheduledTask, referenceDate: Date = new Date()): boolean {
    if (!task.enabled || !task.nextRunAt || task.status === 'RUNNING' || task.status === 'PAUSED' || task.status === 'WAITING_APPROVAL') {
      return false;
    }
    const dueTime = new Date(task.nextRunAt).getTime();
    return dueTime <= referenceDate.getTime();
  }
}
