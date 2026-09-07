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
      name: 'Microsoft Edge',
      executableName: 'msedge.exe',
      processName: 'msedge.exe',
      aliases: ['microsoft edge', 'edge'],
    },
    {
      name: 'Windows Terminal',
      executableName: 'wt.exe',
      processName: 'WindowsTerminal.exe',
      aliases: ['windows terminal', 'terminal', 'wt', 'cmd', 'command prompt', 'powershell'],
    },
    {
      name: 'Spotify Music',
      executableName: 'Spotify.exe',
      processName: 'Spotify.exe',
      aliases: ['spotify', 'spotify music', 'music player', 'spotify.exe'],
    },
    {
      name: 'Notepad',
      executableName: 'notepad.exe',
      processName: 'notepad.exe',
      aliases: ['notepad', 'text editor', 'notes', 'notepad.exe'],
    },
    {
      name: 'Calculator',
      executableName: 'calc.exe',
      processName: 'CalculatorApp.exe',
      aliases: ['calculator', 'calc', 'math', 'calc.exe'],
    },
    {
      name: 'Discord',
      executableName: 'Discord.exe',
      processName: 'Discord.exe',
      aliases: ['discord'],
    },
    {
      name: 'WhatsApp',
      executableName: 'WhatsApp.exe',
      processName: 'WhatsApp.exe',
      aliases: ['whatsapp'],
    },
    {
      name: 'Paint',
      executableName: 'mspaint.exe',
      processName: 'mspaint.exe',
      aliases: ['paint', 'mspaint'],
    },
  ];

  resolve(target: string): ResolvedApplication | null {
    if (!target || typeof target !== 'string') return null;

    // Path traversal check
    if (target.includes('..') || target.includes('/') || target.includes('\\')) {
      return null;
    }

    const clean = target.trim().toLowerCase();
    const found = this.registry.find(
      (app) => app.name.toLowerCase() === clean || app.aliases.includes(clean)
    );
    if (found) return found;

    // Safe dynamic application resolution for alphanumeric application names
    if (/^[a-zA-Z0-9_\-. ]{2,50}$/.test(clean)) {

      const blockedKeywords = ['cmd.exe /c', 'powershell -', 'rmdir', 'del ', 'format '];
      if (blockedKeywords.some((b) => clean.includes(b))) return null;

      return {
        name: target.trim(),
        executableName: `${clean}.exe`,
        processName: `${clean}.exe`,
        aliases: [clean],
      };
    }

    return null;
  }

  isSupported(target: string): boolean {
    return this.resolve(target) !== null;
  }
}

