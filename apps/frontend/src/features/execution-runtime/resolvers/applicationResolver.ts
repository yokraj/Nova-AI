export interface ResolvedApplication {
  name: string;
  executableName: string;
  processName: string;
  defaultPathWindows?: string;
  aliases: string[];
}

export class ApplicationResolver {
  private registry: ResolvedApplication[] = [
    {
      name: 'Visual Studio Code',
      executableName: 'Code.exe',
      processName: 'Code.exe',
      aliases: ['vs code', 'visual studio code', 'code', 'vscode'],
    },
    {
      name: 'Google Chrome',
      executableName: 'chrome.exe',
      processName: 'chrome.exe',
      aliases: ['google chrome', 'chrome', 'browser'],
    },
    {
      name: 'Windows Terminal',
      executableName: 'wt.exe',
      processName: 'WindowsTerminal.exe',
      aliases: ['windows terminal', 'terminal', 'wt', 'cmd'],
    },
    {
      name: 'Spotify Music',
      executableName: 'Spotify.exe',
      processName: 'Spotify.exe',
      aliases: ['spotify', 'spotify music', 'music player'],
    },
    {
      name: 'Notepad',
      executableName: 'notepad.exe',
      processName: 'notepad.exe',
      aliases: ['notepad', 'text editor', 'notes'],
    },
  ];

  resolve(target: string): ResolvedApplication | null {
    if (!target || typeof target !== 'string') return null;

    // Path traversal check
    if (target.includes('..') || target.includes('/') || target.includes('\\')) {
      return null;
    }

    const clean = target.trim().toLowerCase();
    return (
      this.registry.find(
        (app) => app.name.toLowerCase() === clean || app.aliases.includes(clean)
      ) || null
    );
  }

  isSupported(target: string): boolean {
    return this.resolve(target) !== null;
  }
}
