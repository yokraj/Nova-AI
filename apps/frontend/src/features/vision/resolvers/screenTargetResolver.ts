export class ScreenTargetResolver {
  resolveScreenSource(displayId?: string) {
    return {
      type: 'SCREEN' as const,
      sourceId: displayId || 'primary-display',
      name: 'Primary Workstation Screen',
      permission: 'GRANTED' as const,
    };
  }
}
