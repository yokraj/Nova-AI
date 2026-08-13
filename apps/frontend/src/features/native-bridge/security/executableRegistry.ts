export interface TrustedExecutable {
  id: string;
  name: string;
  aliases: string[];
  windowsCommand: string;
  processNames: string[];
}

export class ExecutableRegistry {
  private trustedMap = new Map<string, TrustedExecutable>([
    [
      'VS_CODE',
      {
        id: 'VS_CODE',
        name: 'Visual Studio Code',
        aliases: ['vs code', 'visual studio code', 'code', 'vscode'],
        windowsCommand: 'code',
        processNames: ['Code.exe', 'code.exe'],
      },
    ],
    [
      'CHROME',
      {
        id: 'CHROME',
        name: 'Google Chrome',
        aliases: ['chrome', 'google chrome', 'browser'],
        windowsCommand: 'chrome',
        processNames: ['chrome.exe', 'Chrome.exe'],
      },
    ],
    [
      'TERMINAL',
      {
        id: 'TERMINAL',
        name: 'Windows Terminal',
        aliases: ['terminal', 'windows terminal', 'cmd', 'command prompt', 'powershell'],
        windowsCommand: 'wt',
        processNames: ['WindowsTerminal.exe', 'cmd.exe', 'powershell.exe'],
      },
    ],
    [
      'SPOTIFY',
      {
        id: 'SPOTIFY',
        name: 'Spotify',
        aliases: ['spotify', 'music player'],
        windowsCommand: 'spotify',
        processNames: ['Spotify.exe', 'spotify.exe'],
      },
    ],
    [
      'NOTEPAD',
      {
        id: 'NOTEPAD',
        name: 'Notepad',
        aliases: ['notepad', 'text editor', 'notes'],
        windowsCommand: 'notepad',
        processNames: ['Notepad.exe', 'notepad.exe'],
      },
    ],
  ]);

  resolveExecutable(inputAlias: string): TrustedExecutable | null {
    if (!inputAlias) return null;
    const clean = inputAlias.trim().toLowerCase();

    for (const exec of this.trustedMap.values()) {
      if (exec.id.toLowerCase() === clean) return exec;
      if (exec.aliases.some((alias) => alias.toLowerCase() === clean)) {
        return exec;
      }
    }
    return null;
  }

  isTrustedAlias(inputAlias: string): boolean {
    return this.resolveExecutable(inputAlias) !== null;
  }
}
