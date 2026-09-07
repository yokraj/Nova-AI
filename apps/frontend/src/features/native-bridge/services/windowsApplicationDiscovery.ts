import { execFile } from 'child_process';
import path from 'path';
import fs from 'fs';
import os from 'os';

export interface DiscoveredApplication {
  applicationName: string;
  executablePath: string;
  targetCommand: string;
  processNames: string[];
  source: 'START_MENU' | 'APP_PATHS' | 'STORE_APPX' | 'KNOWN_PATH' | 'EXECUTABLE_REGISTRY';
  confidence: number;
  verified: boolean;
}

export class WindowsApplicationDiscovery {
  private cache: Map<string, DiscoveredApplication> = new Map();
  private isCacheLoaded = false;

  private aliasMap: Record<string, { canonicalName: string; defaultProcesses: string[] }> = {
    'spotify': { canonicalName: 'Spotify', defaultProcesses: ['Spotify.exe', 'spotify.exe'] },
    'spotify music': { canonicalName: 'Spotify', defaultProcesses: ['Spotify.exe', 'spotify.exe'] },
    'music player': { canonicalName: 'Spotify', defaultProcesses: ['Spotify.exe', 'spotify.exe'] },
    'chrome': { canonicalName: 'Google Chrome', defaultProcesses: ['chrome.exe', 'Chrome.exe'] },
    'google chrome': { canonicalName: 'Google Chrome', defaultProcesses: ['chrome.exe', 'Chrome.exe'] },
    'browser': { canonicalName: 'Google Chrome', defaultProcesses: ['chrome.exe', 'msedge.exe'] },
    'vs code': { canonicalName: 'Visual Studio Code', defaultProcesses: ['Code.exe', 'code.exe'] },
    'vscode': { canonicalName: 'Visual Studio Code', defaultProcesses: ['Code.exe', 'code.exe'] },
    'code': { canonicalName: 'Visual Studio Code', defaultProcesses: ['Code.exe', 'code.exe'] },
    'visual studio code': { canonicalName: 'Visual Studio Code', defaultProcesses: ['Code.exe', 'code.exe'] },
    'edge': { canonicalName: 'Microsoft Edge', defaultProcesses: ['msedge.exe'] },
    'microsoft edge': { canonicalName: 'Microsoft Edge', defaultProcesses: ['msedge.exe'] },
    'notepad': { canonicalName: 'Notepad', defaultProcesses: ['Notepad.exe', 'notepad.exe'] },
    'text editor': { canonicalName: 'Notepad', defaultProcesses: ['Notepad.exe', 'notepad.exe'] },
    'calculator': { canonicalName: 'Calculator', defaultProcesses: ['CalculatorApp.exe', 'calc.exe', 'Calculator.exe'] },
    'calc': { canonicalName: 'Calculator', defaultProcesses: ['CalculatorApp.exe', 'calc.exe', 'Calculator.exe'] },
    'terminal': { canonicalName: 'Windows Terminal', defaultProcesses: ['WindowsTerminal.exe', 'cmd.exe', 'powershell.exe'] },
    'windows terminal': { canonicalName: 'Windows Terminal', defaultProcesses: ['WindowsTerminal.exe'] },
    'cmd': { canonicalName: 'Command Prompt', defaultProcesses: ['cmd.exe'] },
    'powershell': { canonicalName: 'PowerShell', defaultProcesses: ['powershell.exe'] },
    'paint': { canonicalName: 'Paint', defaultProcesses: ['mspaint.exe'] },
    'mspaint': { canonicalName: 'Paint', defaultProcesses: ['mspaint.exe'] },
    'discord': { canonicalName: 'Discord', defaultProcesses: ['Discord.exe'] },
    'whatsapp': { canonicalName: 'WhatsApp', defaultProcesses: ['WhatsApp.exe'] },
  };

  private knownPaths: Record<string, { cmd: string; procs: string[]; paths: string[] }> = {
    'spotify': {
      cmd: 'spotify',
      procs: ['Spotify.exe', 'spotify.exe'],
      paths: [
        path.join(os.homedir(), 'AppData', 'Roaming', 'Spotify', 'Spotify.exe'),
        path.join(os.homedir(), 'AppData', 'Local', 'Microsoft', 'WindowsApps', 'Spotify.exe'),
        'C:\\Program Files\\Spotify\\Spotify.exe',
      ],
    },
    'chrome': {
      cmd: 'chrome',
      procs: ['chrome.exe', 'Chrome.exe'],
      paths: [
        'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
        path.join(os.homedir(), 'AppData', 'Local', 'Google', 'Chrome', 'Application', 'chrome.exe'),
      ],
    },
    'vscode': {
      cmd: 'code',
      procs: ['Code.exe', 'code.exe'],
      paths: [
        path.join(os.homedir(), 'AppData', 'Local', 'Programs', 'Microsoft VS Code', 'Code.exe'),
        'C:\\Program Files\\Microsoft VS Code\\Code.exe',
      ],
    },
    'edge': {
      cmd: 'msedge',
      procs: ['msedge.exe'],
      paths: [
        'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
        'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
      ],
    },
    'notepad': {
      cmd: 'notepad',
      procs: ['Notepad.exe', 'notepad.exe'],
      paths: [
        'C:\\Windows\\System32\\notepad.exe',
        'C:\\Windows\\notepad.exe',
      ],
    },
    'calculator': {
      cmd: 'calc',
      procs: ['CalculatorApp.exe', 'calc.exe', 'Calculator.exe'],
      paths: [
        'C:\\Windows\\System32\\calc.exe',
      ],
    },
  };

  private runPowerShell(script: string, timeoutMs = 6000): Promise<string> {
    return new Promise((resolve) => {
      const buffer = Buffer.from(script, 'utf16le');
      const encodedScript = buffer.toString('base64');
      execFile(
        'powershell.exe',
        ['-NoProfile', '-NonInteractive', '-EncodedCommand', encodedScript],
        { timeout: timeoutMs },
        (error, stdout) => {
          resolve(stdout ? stdout.trim() : '');
        }
      );
    });
  }

  async discoverApplications(): Promise<Map<string, DiscoveredApplication>> {
    if (this.isCacheLoaded && this.cache.size > 0) {
      return this.cache;
    }

    // Step 1: Scan Known Application File Paths
    for (const [key, appDef] of Object.entries(this.knownPaths)) {
      for (const p of appDef.paths) {
        if (fs.existsSync(p)) {
          const name = this.aliasMap[key]?.canonicalName || key;
          const discovered: DiscoveredApplication = {
            applicationName: name,
            executablePath: p.replace(/\\/g, '/'),
            targetCommand: `"${p.replace(/\\/g, '/')}"`,
            processNames: appDef.procs,
            source: 'KNOWN_PATH',
            confidence: 0.99,
            verified: true,
          };
          this.cache.set(key, discovered);
          this.cache.set(name.toLowerCase(), discovered);
          break;
        }
      }
    }

    // Step 2: Query Windows Start Menu & AppX Apps via Get-StartApps
    const psScript = `
Get-StartApps | ForEach-Object {
  Write-Output "$($_.Name)|$($_.AppID)"
}
`;
    const startAppsRaw = await this.runPowerShell(psScript);
    if (startAppsRaw) {
      const lines = startAppsRaw.split('\n');
      for (const line of lines) {
        const parts = line.trim().split('|');
        if (parts.length >= 2) {
          const appName = parts[0].trim();
          const appId = parts[1].trim();
          const lowerName = appName.toLowerCase();

          // Check if AppID is a direct path or executable
          let execPath = '';
          let isStoreApp = false;
          if (appId.includes('\\') || appId.includes('/') || appId.endsWith('.exe')) {
            if (fs.existsSync(appId)) {
              execPath = appId.replace(/\\/g, '/');
            }
          } else if (appId.includes('!') || appId.includes('_')) {
            isStoreApp = true;
          }

          const targetCmd = isStoreApp ? `explorer.exe "shell:AppsFolder\\${appId}"` : execPath ? `"${execPath}"` : appId;
          const procNames = [
            appId.endsWith('.exe') ? appId.split('\\').pop() || appId : `${appName.replace(/\s+/g, '')}.exe`,
            `${lowerName}.exe`,
          ];

          const discovered: DiscoveredApplication = {
            applicationName: appName,
            executablePath: execPath || appId,
            targetCommand: targetCmd,
            processNames: procNames,
            source: isStoreApp ? 'STORE_APPX' : 'START_MENU',
            confidence: 0.95,
            verified: true,
          };

          if (!this.cache.has(lowerName)) {
            this.cache.set(lowerName, discovered);
          }
          if (!this.cache.has(appName)) {
            this.cache.set(appName, discovered);
          }
        }
      }
    }

    this.isCacheLoaded = true;
    return this.cache;
  }

  async resolveApplication(inputAlias: string): Promise<DiscoveredApplication | null> {
    if (!inputAlias) return null;
    const clean = inputAlias.trim().toLowerCase();

    // Security Guards: reject path traversal and invalid characters
    if (clean.includes('..') || clean.includes('/') || clean.includes('\\')) {
      return null;
    }

    // 1. Check alias normalization map
    const aliasInfo = this.aliasMap[clean];
    const canonicalName = aliasInfo ? aliasInfo.canonicalName : inputAlias;

    // Ensure discovery cache is loaded
    await this.discoverApplications();

    // 2. Check cache by alias or canonical name
    let found = this.cache.get(clean) || this.cache.get(canonicalName.toLowerCase()) || this.cache.get(canonicalName);

    if (!found) {
      // Partial match search in cache
      for (const [key, app] of this.cache.entries()) {
        if (key.includes(clean) || app.applicationName.toLowerCase().includes(clean)) {
          found = app;
          break;
        }
      }
    }

    if (found) {
      // Ensure process names include alias defaults if available
      const procs = new Set([...found.processNames, ...(aliasInfo?.defaultProcesses || [])]);
      return {
        ...found,
        applicationName: canonicalName,
        processNames: Array.from(procs),
        confidence: Math.max(found.confidence, 0.95),
      };
    }

    // 3. Fallback for standard system apps if present in PATH / system
    if (aliasInfo) {
      return {
        applicationName: aliasInfo.canonicalName,
        executablePath: clean,
        targetCommand: clean,
        processNames: aliasInfo.defaultProcesses,
        source: 'EXECUTABLE_REGISTRY',
        confidence: 0.90,
        verified: true,
      };
    }

    return null;
  }
}
