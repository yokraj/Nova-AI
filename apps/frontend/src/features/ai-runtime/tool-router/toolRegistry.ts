export interface RegisteredTool {
  name: string;
  domain: 'filesystem' | 'application' | 'browser' | 'vision' | 'system' | 'memory' | 'knowledge' | 'computer';
  description: string;
  riskLevel: 'SAFE' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  parametersSchema: Record<string, string>;
}

export class ToolRegistry {
  private tools: Map<string, RegisteredTool> = new Map();

  constructor() {
    this.registerDefaults();
  }

  private registerDefaults() {
    const defaultTools: RegisteredTool[] = [
      {
        name: 'filesystem.read_directory',
        domain: 'filesystem',
        description: 'Read directory contents on local disk',
        riskLevel: 'SAFE',
        parametersSchema: { path: 'string' },
      },
      {
        name: 'filesystem.create_directory',
        domain: 'filesystem',
        description: 'Create directory on local disk',
        riskLevel: 'LOW',
        parametersSchema: { path: 'string' },
      },
      {
        name: 'filesystem.create_file',
        domain: 'filesystem',
        description: 'Create file on local disk',
        riskLevel: 'LOW',
        parametersSchema: { path: 'string' },
      },
      {
        name: 'filesystem.write_file',
        domain: 'filesystem',
        description: 'Write text content to file on local disk',
        riskLevel: 'LOW',
        parametersSchema: { path: 'string', content: 'string' },
      },
      {
        name: 'filesystem.read_file',
        domain: 'filesystem',
        description: 'Read file text content from local disk',
        riskLevel: 'SAFE',
        parametersSchema: { path: 'string' },
      },
      {
        name: 'filesystem.delete_file',
        domain: 'filesystem',
        description: 'Delete file from local disk',
        riskLevel: 'HIGH',
        parametersSchema: { path: 'string' },
      },
      {
        name: 'application.open',
        domain: 'application',
        description: 'Launch desktop application',
        riskLevel: 'LOW',
        parametersSchema: { applicationName: 'string' },
      },
      {
        name: 'application.verify_running',
        domain: 'application',
        description: 'Verify application process is running',
        riskLevel: 'SAFE',
        parametersSchema: { applicationName: 'string' },
      },
      {
        name: 'browser.open',
        domain: 'browser',
        description: 'Initialize browser and navigate to URL',
        riskLevel: 'LOW',
        parametersSchema: { url: 'string' },
      },
      {
        name: 'browser.navigate',
        domain: 'browser',
        description: 'Navigate active browser tab to URL',
        riskLevel: 'SAFE',
        parametersSchema: { url: 'string' },
      },
      {
        name: 'browser.connect',
        domain: 'browser',
        description: 'Connect to local Chrome CDP debugging endpoint',
        riskLevel: 'SAFE',
        parametersSchema: { port: 'number' },
      },
      {
        name: 'browser.list_tabs',
        domain: 'browser',
        description: 'List active open browser tabs',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'browser.open_tab',
        domain: 'browser',
        description: 'Open a new browser tab with optional target URL',
        riskLevel: 'SAFE',
        parametersSchema: { url: 'string' },
      },
      {
        name: 'browser.close_tab',
        domain: 'browser',
        description: 'Close active or specified browser tab',
        riskLevel: 'LOW',
        parametersSchema: { tabId: 'string' },
      },
      {
        name: 'browser.switch_tab',
        domain: 'browser',
        description: 'Switch active foreground browser tab',
        riskLevel: 'SAFE',
        parametersSchema: { tabId: 'string' },
      },
      {
        name: 'browser.read_page',
        domain: 'browser',
        description: 'Inspect structured DOM and visible text of current page',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'browser.find_text',
        domain: 'browser',
        description: 'Search target text content within active DOM page',
        riskLevel: 'SAFE',
        parametersSchema: { query: 'string' },
      },
      {
        name: 'browser.click',
        domain: 'browser',
        description: 'Click target DOM element or text query via CDP',
        riskLevel: 'LOW',
        parametersSchema: { targetQuery: 'string', selector: 'string' },
      },
      {
        name: 'browser.type_text',
        domain: 'browser',
        description: 'Type text into focused DOM input element via CDP',
        riskLevel: 'MEDIUM',
        parametersSchema: { text: 'string', selector: 'string' },
      },
      {
        name: 'browser.scroll',
        domain: 'browser',
        description: 'Scroll active browser page viewport',
        riskLevel: 'SAFE',
        parametersSchema: { deltaY: 'number' },
      },
      {
        name: 'browser.wait_for_element',
        domain: 'browser',
        description: 'Wait for target element matching selector to appear in DOM',
        riskLevel: 'SAFE',
        parametersSchema: { selector: 'string', timeoutMs: 'number' },
      },
      {
        name: 'browser.screenshot',
        domain: 'browser',
        description: 'Capture screenshot of active browser viewport',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'vision.observe_screen',
        domain: 'vision',
        description: 'Capture active screen display and detect visual elements',
        riskLevel: 'LOW',
        parametersSchema: { source: 'string' },
      },
      {
        name: 'system.get_info',
        domain: 'system',
        description: 'Retrieve Windows system information (CPU, RAM, OS version, uptime)',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'system.cpu_status',
        domain: 'system',
        description: 'Query CPU core usage and model status',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'system.memory_status',
        domain: 'system',
        description: 'Query RAM total, free, and percentage memory usage',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'system.storage_status',
        domain: 'system',
        description: 'Query local disk drive storage status',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'system.battery_status',
        domain: 'system',
        description: 'Query power battery percentage and AC charging state',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'system.volume_get',
        domain: 'system',
        description: 'Query current Windows audio volume level',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'system.volume_set',
        domain: 'system',
        description: 'Set Windows audio volume level (0-100)',
        riskLevel: 'LOW',
        parametersSchema: { level: 'number' },
      },
      {
        name: 'system.volume_mute',
        domain: 'system',
        description: 'Mute Windows system audio output',
        riskLevel: 'LOW',
        parametersSchema: {},
      },
      {
        name: 'system.volume_unmute',
        domain: 'system',
        description: 'Unmute Windows system audio output',
        riskLevel: 'LOW',
        parametersSchema: {},
      },
      {
        name: 'system.brightness_get',
        domain: 'system',
        description: 'Query current display brightness level',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'system.brightness_set',
        domain: 'system',
        description: 'Set display brightness level (0-100)',
        riskLevel: 'LOW',
        parametersSchema: { level: 'number' },
      },
      {
        name: 'system.network_status',
        domain: 'system',
        description: 'Query active network interfaces and connectivity state',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'system.wifi_set',
        domain: 'system',
        description: 'Enable or disable Wi-Fi network interface',
        riskLevel: 'MEDIUM',
        parametersSchema: { enabled: 'boolean' },
      },
      {
        name: 'system.bluetooth_set',
        domain: 'system',
        description: 'Enable or disable Bluetooth radio adapter',
        riskLevel: 'MEDIUM',
        parametersSchema: { enabled: 'boolean' },
      },
      {
        name: 'system.power_lock',
        domain: 'system',
        description: 'Lock Windows workstation screen',
        riskLevel: 'HIGH',
        parametersSchema: {},
      },
      {
        name: 'system.power_sleep',
        domain: 'system',
        description: 'Put computer into low power sleep mode',
        riskLevel: 'HIGH',
        parametersSchema: {},
      },
      {
        name: 'system.power_restart',
        domain: 'system',
        description: 'Restart Windows operating system',
        riskLevel: 'HIGH',
        parametersSchema: {},
      },
      {
        name: 'system.power_shutdown',
        domain: 'system',
        description: 'Shut down Windows operating system',
        riskLevel: 'CRITICAL',
        parametersSchema: {},
      },
      {
        name: 'system.power_signout',
        domain: 'system',
        description: 'Sign out current Windows user session',
        riskLevel: 'HIGH',
        parametersSchema: {},
      },
      {
        name: 'system.process_list',
        domain: 'system',
        description: 'List active running processes from Windows tasklist',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'system.process_find',
        domain: 'system',
        description: 'Find target process in active Windows tasklist',
        riskLevel: 'SAFE',
        parametersSchema: { processName: 'string' },
      },
      {
        name: 'system.process_terminate',
        domain: 'system',
        description: 'Terminate active application process by name or PID',
        riskLevel: 'MEDIUM',
        parametersSchema: { processName: 'string' },
      },
      {
        name: 'system.screenshot_capture',
        domain: 'system',
        description: 'Capture screenshot of active display screen',
        riskLevel: 'LOW',
        parametersSchema: {},
      },
      {
        name: 'computer.screenshot',
        domain: 'computer',
        description: 'Capture screenshot reference of desktop screen',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'computer.observe_screen',
        domain: 'computer',
        description: 'Capture screen and detect visible UI elements with OCR',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'computer.click',
        domain: 'computer',
        description: 'Click mouse cursor at target element or coordinates',
        riskLevel: 'LOW',
        parametersSchema: { targetQuery: 'string', x: 'number', y: 'number' },
      },
      {
        name: 'computer.double_click',
        domain: 'computer',
        description: 'Double click mouse cursor at target element or coordinates',
        riskLevel: 'LOW',
        parametersSchema: { targetQuery: 'string', x: 'number', y: 'number' },
      },
      {
        name: 'computer.right_click',
        domain: 'computer',
        description: 'Right click mouse cursor at target element or coordinates',
        riskLevel: 'LOW',
        parametersSchema: { targetQuery: 'string', x: 'number', y: 'number' },
      },
      {
        name: 'computer.type_text',
        domain: 'computer',
        description: 'Type text into focused control or input field',
        riskLevel: 'MEDIUM',
        parametersSchema: { text: 'string' },
      },
      {
        name: 'computer.press_key',
        domain: 'computer',
        description: 'Press single keyboard key (Enter, Tab, Esc, Backspace, etc.)',
        riskLevel: 'LOW',
        parametersSchema: { key: 'string' },
      },
      {
        name: 'computer.key_combination',
        domain: 'computer',
        description: 'Press keyboard shortcut combination (Ctrl+C, Ctrl+V, etc.)',
        riskLevel: 'LOW',
        parametersSchema: { keys: 'string' },
      },
      {
        name: 'computer.copy',
        domain: 'computer',
        description: 'Copy selected text or item to clipboard (Ctrl+C)',
        riskLevel: 'LOW',
        parametersSchema: {},
      },
      {
        name: 'computer.paste',
        domain: 'computer',
        description: 'Paste clipboard content into active control (Ctrl+V)',
        riskLevel: 'MEDIUM',
        parametersSchema: {},
      },
      {
        name: 'computer.list_windows',
        domain: 'computer',
        description: 'List active application desktop windows',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'computer.get_active_window',
        domain: 'computer',
        description: 'Get details of currently active foreground window',
        riskLevel: 'SAFE',
        parametersSchema: {},
      },
      {
        name: 'computer.focus_window',
        domain: 'computer',
        description: 'Bring target application window to foreground focus',
        riskLevel: 'LOW',
        parametersSchema: { windowTitle: 'string', processName: 'string' },
      },
      {
        name: 'computer.close_window',
        domain: 'computer',
        description: 'Close target desktop application window',
        riskLevel: 'MEDIUM',
        parametersSchema: { windowTitle: 'string', processName: 'string' },
      },
      {
        name: 'computer.switch_application',
        domain: 'computer',
        description: 'Switch active foreground application focus',
        riskLevel: 'LOW',
        parametersSchema: { applicationName: 'string' },
      },
    ];

    for (const tool of defaultTools) {
      this.tools.set(tool.name, tool);
    }
  }

  getTool(name: string): RegisteredTool | undefined {
    return this.tools.get(name);
  }

  hasTool(name: string): boolean {
    return this.tools.has(name);
  }

  getAllTools(): RegisteredTool[] {
    return Array.from(this.tools.values());
  }
}
