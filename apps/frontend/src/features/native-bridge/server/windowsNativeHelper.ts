import { execFile } from 'child_process';
import path from 'path';
import fs from 'fs';
import os from 'os';

export interface WindowInfo {
  processName: string;
  title: string;
  handle?: string;
  processId?: number;
  bounds?: { x: number; y: number; width: number; height: number };
}

export class WindowsNativeHelper {
  private protectedProcesses = [
    'explorer.exe',
    'lsass.exe',
    'csrss.exe',
    'svchost.exe',
    'smss.exe',
    'services.exe',
    'wininit.exe',
    'system',
    'dwm.exe',
  ];

  public isProtectedProcess(name: string): boolean {
    const lower = (name || '').toLowerCase();
    return this.protectedProcesses.some((p) => lower.includes(p));
  }

  private elevatedApps = [
    'regedit',
    'regedit.exe',
    'mmc',
    'mmc.exe',
    'taskmgr',
    'taskmgr.exe',
    'diskmgmt.msc',
    'cmd_admin',
    'powershell_admin',
  ];

  public isElevatedApplication(nameOrAlias: string): boolean {
    const lower = (nameOrAlias || '').toLowerCase().trim();
    return this.elevatedApps.some((a) => lower.includes(a));
  }

  async isCurrentProcessElevated(): Promise<boolean> {
    const psScript = `([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)`;
    const res = await this.runPowerShell(psScript);
    return res.stdout.toLowerCase() === 'true';
  }

  async isProcessElevated(procNameOrId: string | number): Promise<boolean> {
    const query = typeof procNameOrId === 'number' ? `-Id ${procNameOrId}` : `-Name "${procNameOrId}"`;
    const psScript = `
try {
  $p = Get-Process ${query} -ErrorAction Stop | Select-Object -First 1
  if ($p.Path) {
    return [bool]($p.Handle)
  }
  return $false
} catch {
  return $false
}
`;
    const res = await this.runPowerShell(psScript);
    return res.stdout.toLowerCase() === 'true';
  }

  async launchElevatedProcess(executableOrCmd: string): Promise<boolean> {
    const escaped = executableOrCmd.replace(/"/g, '""');
    const psScript = `Start-Process -FilePath "${escaped}" -Verb RunAs`;
    const res = await this.runPowerShell(psScript, 10000);
    return res.code === 0;
  }

  private runPowerShell(script: string, timeoutMs = 8000): Promise<{ stdout: string; stderr: string; code: number }> {
    return new Promise((resolve) => {
      // Encode command in base64 to avoid quotes/escaping issues in powershell CLI
      const buffer = Buffer.from(script, 'utf16le');
      const encodedScript = buffer.toString('base64');
      execFile(
        'powershell.exe',
        ['-NoProfile', '-NonInteractive', '-EncodedCommand', encodedScript],
        { timeout: timeoutMs },
        (error, stdout, stderr) => {
          resolve({
            stdout: stdout ? stdout.trim() : '',
            stderr: stderr ? stderr.trim() : '',
            code: error ? (typeof error.code === 'number' ? error.code : 1) : 0,
          });
        }
      );
    });
  }

  async mouseMove(x: number, y: number): Promise<boolean> {
    const psScript = `
Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);' -Name User32 -Namespace Win32
[Win32.User32]::SetCursorPos(${Math.round(x)}, ${Math.round(y)})
`;
    const res = await this.runPowerShell(psScript);
    return res.code === 0;
  }

  async mouseClick(
    x?: number,
    y?: number,
    button: 'left' | 'right' | 'middle' = 'left',
    doubleClick = false,
    scrollDelta = 0
  ): Promise<boolean> {
    let movePart = '';
    if (x !== undefined && y !== undefined) {
      movePart = `[Win32.User32]::SetCursorPos(${Math.round(x)}, ${Math.round(y)}); Start-Sleep -Milliseconds 20;`;
    }

    let flagsDown = 0x0002; // LEFTDOWN
    let flagsUp = 0x0004; // LEFTUP

    if (button === 'right') {
      flagsDown = 0x0008; // RIGHTDOWN
      flagsUp = 0x0010; // RIGHTUP
    } else if (button === 'middle') {
      flagsDown = 0x0020; // MIDDLEDOWN
      flagsUp = 0x0040; // MIDDLEUP
    }

    let clickLoop = `[Win32.User32]::mouse_event(${flagsDown}, 0, 0, 0, 0); [Win32.User32]::mouse_event(${flagsUp}, 0, 0, 0, 0);`;
    if (doubleClick) {
      clickLoop += ` Start-Sleep -Milliseconds 50; [Win32.User32]::mouse_event(${flagsDown}, 0, 0, 0, 0); [Win32.User32]::mouse_event(${flagsUp}, 0, 0, 0, 0);`;
    }

    if (scrollDelta !== 0) {
      const WHEEL_FLAG = 0x0800;
      clickLoop = `[Win32.User32]::mouse_event(${WHEEL_FLAG}, 0, 0, ${Math.round(scrollDelta)}, 0);`;
    }

    const psScript = `
Add-Type -MemberDefinition '
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(int dwFlags, int dx, int dy, int dwData, int dwExtraInfo);
' -Name User32 -Namespace Win32
${movePart}
${clickLoop}
`;
    const res = await this.runPowerShell(psScript);
    return res.code === 0;
  }

  async keyboardType(text: string): Promise<boolean> {
    if (!text) return true;
    const escapedText = text
      .replace(/[{}+^%~()]/g, '{$&}')
      .replace(/"/g, '""');


    const psScript = `
try {
  $wshell = New-Object -ComObject WScript.Shell
  $wshell.SendKeys("${escapedText}")
} catch {
  Add-Type -AssemblyName System.Windows.Forms
  [System.Windows.Forms.SendKeys]::SendWait("${escapedText}")
}
`;
    const res = await this.runPowerShell(psScript);
    return res.code === 0;
  }

  async keyboardPress(keyName: string): Promise<boolean> {
    if (!keyName) return true;

    const keyMap: Record<string, string> = {
      enter: '{ENTER}',
      return: '{ENTER}',
      tab: '{TAB}',
      esc: '{ESC}',
      escape: '{ESC}',
      backspace: '{BACKSPACE}',
      bs: '{BACKSPACE}',
      delete: '{DELETE}',
      del: '{DELETE}',
      space: ' ',
      up: '{UP}',
      down: '{DOWN}',
      left: '{LEFT}',
      right: '{RIGHT}',
      home: '{HOME}',
      end: '{END}',
      pageup: '{PGUP}',
      pagedown: '{PGDN}',
    };

    const targetKey = keyMap[keyName.toLowerCase()] || keyName;
    const psScript = `
try {
  $wshell = New-Object -ComObject WScript.Shell
  $wshell.SendKeys("${targetKey}")
} catch {
  Add-Type -AssemblyName System.Windows.Forms
  [System.Windows.Forms.SendKeys]::SendWait("${targetKey}")
}
`;
    const res = await this.runPowerShell(psScript);
    return res.code === 0;
  }

  async keyboardCombination(keys: string[]): Promise<boolean> {
    if (!keys || keys.length === 0) return true;

    let sendStr = '';
    const ctrl = keys.some((k) => k.toLowerCase() === 'ctrl' || k.toLowerCase() === 'control');
    const alt = keys.some((k) => k.toLowerCase() === 'alt');
    const shift = keys.some((k) => k.toLowerCase() === 'shift');
    const win = keys.some((k) => k.toLowerCase() === 'win' || k.toLowerCase() === 'cmd');

    const regularKey = keys.find((k) => !['ctrl', 'control', 'alt', 'shift', 'win', 'cmd'].includes(k.toLowerCase())) || '';

    if (ctrl) sendStr += '^';
    if (alt) sendStr += '%';
    if (shift) sendStr += '+';

    let keyPart = regularKey.toLowerCase();
    if (keyPart === 'c') keyPart = 'c';
    else if (keyPart === 'v') keyPart = 'v';
    else if (keyPart === 'a') keyPart = 'a';
    else if (keyPart === 's') keyPart = 's';
    else if (keyPart === 'z') keyPart = 'z';
    else if (keyPart === 'y') keyPart = 'y';
    else if (keyPart === 'f') keyPart = 'f';
    else if (keyPart === 'tab') keyPart = '{TAB}';
    else if (keyPart === 'enter') keyPart = '{ENTER}';
    else if (keyPart.length === 1) keyPart = keyPart.toLowerCase();

    sendStr += keyPart;

    if (win) {
      const psScriptWin = `
Add-Type -MemberDefinition '
  [DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, int dwExtraInfo);
' -Name User32 -Namespace Win32
[Win32.User32]::keybd_event(0x5B, 0, 0, 0)
$wshell = New-Object -ComObject WScript.Shell
$wshell.SendKeys("${keyPart}")
[Win32.User32]::keybd_event(0x5B, 0, 2, 0)
`;
      const res = await this.runPowerShell(psScriptWin);
      return res.code === 0;
    }

    const psScript = `
try {
  $wshell = New-Object -ComObject WScript.Shell
  $wshell.SendKeys("${sendStr}")
} catch {
  Add-Type -AssemblyName System.Windows.Forms
  [System.Windows.Forms.SendKeys]::SendWait("${sendStr}")
}
`;
    const res = await this.runPowerShell(psScript);
    return res.code === 0;
  }


  async clipboardGet(): Promise<string> {
    const psScript = `Get-Clipboard`;
    const res = await this.runPowerShell(psScript);
    return res.stdout || '';
  }

  async clipboardSet(text: string): Promise<boolean> {
    const escaped = text.replace(/"/g, '""');
    const psScript = `Set-Clipboard -Value "${escaped}"`;
    const res = await this.runPowerShell(psScript);
    return res.code === 0;
  }

  async captureScreenshot(): Promise<{ width: number; height: number; filePath: string } | null> {
    const outDir = path.join(os.tmpdir(), 'nova_screenshots');
    if (!fs.existsSync(outDir)) {
      fs.mkdirSync(outDir, { recursive: true });
    }
    const targetFile = path.join(outDir, `shot_${Date.now()}.png`).replace(/\\/g, '/');

    const psScript = `
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$vScreen = [System.Windows.Forms.SystemInformation]::VirtualScreen
$left = $vScreen.Left
$top = $vScreen.Top
$width = $vScreen.Width
$height = $vScreen.Height
if ($width -le 0 -or $height -le 0) {
  $screen = [System.Windows.Forms.Screen]::PrimaryScreen
  $left = $screen.Bounds.X
  $top = $screen.Bounds.Y
  $width = $screen.Bounds.Width
  $height = $screen.Bounds.Height
}
$bitmap = New-Object System.Drawing.Bitmap $width, $height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($left, $top, 0, 0, $bitmap.Size)
$bitmap.Save("${targetFile}", [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bitmap.Dispose()
Write-Output "$width,$height,${targetFile}"
`;
    const res = await this.runPowerShell(psScript);
    if (res.code === 0 && res.stdout) {
      const parts = res.stdout.trim().split(',');
      if (parts.length >= 3) {
        return {
          width: parseInt(parts[0], 10) || 1920,
          height: parseInt(parts[1], 10) || 1080,
          filePath: parts[2].trim(),
        };
      }
    }
    return null;
  }

  async getActiveWindow(): Promise<WindowInfo | null> {
    const psScript = `
Add-Type -MemberDefinition '
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
  public struct RECT { public int Left; public int Top; public int Right; public int Bottom; }
' -Name User32 -Namespace Win32

$hwnd = [Win32.User32]::GetForegroundWindow()
if ($hwnd -eq [IntPtr]::Zero) { exit 1 }

$sb = New-Object System.Text.StringBuilder 512
[void][Win32.User32]::GetWindowText($hwnd, $sb, 512)
$title = $sb.ToString()

$pid = 0
[void][Win32.User32]::GetWindowThreadProcessId($hwnd, [ref]$pid)
$proc = Get-Process -Id $pid -ErrorAction SilentlyContinue

$rect = New-Object Win32.User32+RECT
[void][Win32.User32]::GetWindowRect($hwnd, [ref]$rect)

$w = $rect.Right - $rect.Left
$h = $rect.Bottom - $rect.Top

Write-Output "$($proc.ProcessName)|$title|$pid|$($rect.Left)|$($rect.Top)|$w|$h"
`;
    const res = await this.runPowerShell(psScript);
    if (res.code === 0 && res.stdout) {
      const parts = res.stdout.split('|');
      if (parts.length >= 7) {
        return {
          processName: parts[0] ? `${parts[0]}.exe` : 'unknown.exe',
          title: parts[1] || 'Foreground Window',
          processId: parseInt(parts[2], 10) || 0,
          bounds: {
            x: parseInt(parts[3], 10) || 0,
            y: parseInt(parts[4], 10) || 0,
            width: parseInt(parts[5], 10) || 0,
            height: parseInt(parts[6], 10) || 0,
          },
        };
      }
    }
    return null;
  }

  async getWindowList(): Promise<WindowInfo[]> {
    const psScript = `
Get-Process | Where-Object { $_.MainWindowTitle -ne "" } | ForEach-Object {
  Write-Output "$($_.ProcessName)|$($_.MainWindowTitle)|$($_.Id)"
}
`;
    const res = await this.runPowerShell(psScript);
    if (res.code === 0 && res.stdout) {
      const lines = res.stdout.split('\n');
      const windows: WindowInfo[] = [];
      for (const line of lines) {
        const parts = line.trim().split('|');
        if (parts.length >= 3 && parts[1]) {
          windows.push({
            processName: `${parts[0]}.exe`,
            title: parts[1],
            processId: parseInt(parts[2], 10) || 0,
          });
        }
      }
      return windows;
    }
    return [];
  }

  async focusWindow(targetNameOrTitle: string): Promise<boolean> {
    if (!targetNameOrTitle) return false;
    const escaped = targetNameOrTitle.replace(/'/g, "''").replace(/\.exe$/i, '');

    const psScript = `
$found = $false
for ($i = 0; $i -lt 8; $i++) {
  $procs = Get-Process | Where-Object { $_.ProcessName -like "*${escaped}*" -or $_.MainWindowTitle -like "*${escaped}*" }
  if ($procs) {
    foreach ($target in $procs) {
      if ($target.MainWindowHandle -ne [IntPtr]::Zero) {
        Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);' -Name User32 -Namespace Win32 -ErrorAction SilentlyContinue
        [Win32.User32]::ShowWindow($target.MainWindowHandle, 9)
        [Win32.User32]::SetForegroundWindow($target.MainWindowHandle)
      }
      $wshell = New-Object -ComObject WScript.Shell
      if ($wshell.AppActivate($target.Id)) {
        Write-Output "SUCCESS"
        $found = $true
        break
      }
    }
  }
  if ($found) { break }
  Start-Sleep -Milliseconds 250
}
if (-not $found) { exit 1 }
`;
    const res = await this.runPowerShell(psScript);
    return res.stdout.includes('SUCCESS');
  }


  async setWindowState(targetNameOrTitle: string, state: 'MINIMIZE' | 'MAXIMIZE' | 'RESTORE' | 'CLOSE'): Promise<boolean> {
    if (!targetNameOrTitle) return false;

    if (this.isProtectedProcess(targetNameOrTitle)) {
      return false;
    }

    const escaped = targetNameOrTitle.replace(/'/g, "''").replace(/\.exe$/i, '');
    const cmdShow = state === 'MINIMIZE' ? 6 : state === 'MAXIMIZE' ? 3 : 9;

    if (state === 'CLOSE') {
      const psScriptClose = `
$procs = Get-Process | Where-Object { $_.ProcessName -like "*${escaped}*" -or $_.MainWindowTitle -like "*${escaped}*" }
if ($procs) {
  foreach ($p in $procs) {
    $p.CloseMainWindow() | Out-Null
  }
  Write-Output "CLOSED"
} else {
  exit 1
}
`;
      const res = await this.runPowerShell(psScriptClose);
      return res.stdout.includes('CLOSED');
    }

    const psScript = `
Add-Type -MemberDefinition '
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
' -Name User32 -Namespace Win32

$procs = Get-Process | Where-Object { $_.ProcessName -like "*${escaped}*" -or $_.MainWindowTitle -like "*${escaped}*" }
if ($procs) {
  foreach ($p in $procs) {
    if ($p.MainWindowHandle -ne [IntPtr]::Zero) {
      [Win32.User32]::ShowWindow($p.MainWindowHandle, ${cmdShow})
    }
  }
  Write-Output "SUCCESS"
} else {
  exit 1
}
`;
    const res = await this.runPowerShell(psScript);
    return res.stdout.includes('SUCCESS');
  }
}

