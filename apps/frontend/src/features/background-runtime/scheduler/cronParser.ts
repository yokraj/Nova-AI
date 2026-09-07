export class CronParser {
  static parseNextRun(cronExpression: string, referenceDate: Date = new Date()): Date {
    const parts = cronExpression.trim().split(/\s+/);
    if (parts.length < 5) {
      // Fallback: 1 hour in future if invalid cron
      return new Date(referenceDate.getTime() + 3600 * 1000);
    }

    const [minute, hour, dayOfMonth, month, dayOfWeek] = parts;
    const next = new Date(referenceDate.getTime());
    next.setSeconds(0, 0);

    // If minute is interval e.g. */5
    if (minute.startsWith('*/')) {
      const step = parseInt(minute.substring(2), 10) || 5;
      const currentMin = next.getMinutes();
      const rem = currentMin % step;
      const addMins = step - rem;
      next.setMinutes(currentMin + addMins);
      return next;
    }

    // Default step forward by 1 minute to compute next valid slot
    next.setMinutes(next.getMinutes() + 1);

    const targetHour = hour === '*' ? undefined : parseInt(hour, 10);
    const targetMin = minute === '*' ? 0 : parseInt(minute, 10);

    if (targetHour !== undefined && !isNaN(targetHour)) {
      if (next.getHours() > targetHour || (next.getHours() === targetHour && next.getMinutes() > targetMin)) {
        next.setDate(next.getDate() + 1);
      }
      next.setHours(targetHour);
    }

    if (!isNaN(targetMin)) {
      next.setMinutes(targetMin);
    }

    return next;
  }
}
