export class WorkflowNormalizer {
  normalizeGoalText(rawGoal: string): string {
    let normalized = rawGoal.trim();

    // Application aliases
    normalized = normalized.replace(/\b(launch|start|open up|run)\b/gi, 'Open');
    normalized = normalized.replace(/\b(visual studio code)\b/gi, 'VS Code');
    normalized = normalized.replace(/\b(google chrome)\b/gi, 'Chrome');

    // Filesystem aliases
    normalized = normalized.replace(/\b(make a folder|create directory|make directory)\b/gi, 'Create folder');
    normalized = normalized.replace(/\b(create a file|make file|touch file)\b/gi, 'Create file');

    // System control aliases
    normalized = normalized.replace(/\b(turn up volume|increase volume|sound up)\b/gi, 'Set volume');
    normalized = normalized.replace(/\b(reboot|restart computer)\b/gi, 'Restart system');

    return normalized;
  }

  normalizeToolName(toolName: string): string {
    const map: Record<string, string> = {
      'app.launch': 'application.open',
      'app.open': 'application.open',
      'fs.mkdir': 'filesystem.create_directory',
      'fs.create_file': 'filesystem.create_file',
      'fs.write': 'filesystem.write_file',
      'fs.read': 'filesystem.read_file',
      'sys.volume': 'system.volume_set',
      'web.open': 'browser.open',
      'web.navigate': 'browser.navigate',
    };

    return map[toolName] || toolName;
  }

  normalizePathTarget(path: string): string {
    if (!path) return path;

    // Convert Windows backslashes for normalization
    let norm = path.replace(/\\/g, '/');

    // Normalize user desktop references
    norm = norm.replace(/^([A-Za-z]):\/Users\/[^/]+\/Desktop\//i, 'Desktop/');
    norm = norm.replace(/^([A-Za-z]):\/Users\/[^/]+\/Documents\//i, 'Documents/');
    norm = norm.replace(/^([A-Za-z]):\/Users\/[^/]+\/Downloads\//i, 'Downloads/');

    return norm;
  }
}
