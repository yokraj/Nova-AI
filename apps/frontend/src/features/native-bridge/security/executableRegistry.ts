import { WindowsApplicationDiscovery } from '../services/windowsApplicationDiscovery';


export interface TrustedExecutable {
  id: string;
  name: string;
  aliases: string[];
  windowsCommand: string;
  processNames: string[];
  source?: string;
  confidence?: number;
}

export class ExecutableRegistry {
  private discovery = new WindowsApplicationDiscovery();
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
        aliases: ['terminal', 'windows terminal', 'cmd', 'command prompt', 'powershell', 'wt'],
        windowsCommand: 'wt',
        processNames: ['WindowsTerminal.exe', 'cmd.exe', 'powershell.exe'],
      },
    ],
    [
      'SPOTIFY',
      {
        id: 'SPOTIFY',
        name: 'Spotify',
        aliases: ['spotify', 'spotify music', 'music player', 'spotify.exe'],
        windowsCommand: 'spotify',
        processNames: ['Spotify.exe', 'spotify.exe'],
      },
    ],
    [
      'NOTEPAD',
      {
        id: 'NOTEPAD',
        name: 'Notepad',
        aliases: ['notepad', 'text editor', 'notes', 'notepad.exe'],
        windowsCommand: 'notepad',
        processNames: ['Notepad.exe', 'notepad.exe'],
      },
    ],
    [
      'CALCULATOR',
      {
        id: 'CALCULATOR',
        name: 'Calculator',
        aliases: ['calc', 'calculator', 'math', 'calc.exe'],
        windowsCommand: 'calc',
        processNames: ['CalculatorApp.exe', 'calc.exe', 'Calculator.exe'],
      },
    ],
  ]);

  resolveExecutable(inputAlias: string): TrustedExecutable | null {
    if (!inputAlias) return null;
    const clean = inputAlias.trim().toLowerCase();

    // Rejection guard: path traversal
    if (clean.includes('..') || clean.includes('/') || clean.includes('\\')) {
      return null;
    }

    for (const exec of this.trustedMap.values()) {
      if (exec.id.toLowerCase() === clean) return exec;
      if (exec.aliases.some((alias) => alias.toLowerCase() === clean)) {
        return exec;
      }
    }

    const safeSystemApps: Record<string, { name: string; cmd: string; procs: string[] }> = {
      'mspaint': { name: 'Paint', cmd: 'mspaint', procs: ['mspaint.exe'] },
      'mspaint.exe': { name: 'Paint', cmd: 'mspaint', procs: ['mspaint.exe'] },
      'cmd': { name: 'Command Prompt', cmd: 'cmd', procs: ['cmd.exe'] },
      'cmd.exe': { name: 'Command Prompt', cmd: 'cmd', procs: ['cmd.exe'] },
      'powershell': { name: 'PowerShell', cmd: 'powershell', procs: ['powershell.exe'] },
      'powershell.exe': { name: 'PowerShell', cmd: 'powershell', procs: ['powershell.exe'] },
    };

    if (safeSystemApps[clean]) {
      const app = safeSystemApps[clean];
      return {
        id: clean.toUpperCase(),
        name: app.name,
        aliases: [clean],
        windowsCommand: app.cmd,
        processNames: app.procs,
      };
    }

    return null;
  }

  async resolveExecutableAsync(inputAlias: string): Promise<TrustedExecutable | null> {
    const syncRes = this.resolveExecutable(inputAlias);
    if (syncRes) return syncRes;

    const discovered = await this.discovery.resolveApplication(inputAlias);
    if (discovered) {
      return {
        id: discovered.applicationName.toUpperCase().replace(/\s+/g, '_'),
        name: discovered.applicationName,
        aliases: [inputAlias.toLowerCase(), discovered.applicationName.toLowerCase()],
        windowsCommand: discovered.targetCommand,
        processNames: discovered.processNames,
        source: discovered.source,
        confidence: discovered.confidence,
      };
    }

    return null;
  }

  isTrustedAlias(inputAlias: string): boolean {
    return this.resolveExecutable(inputAlias) !== null;
  }
}



