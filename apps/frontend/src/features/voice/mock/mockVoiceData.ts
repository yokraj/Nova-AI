export const MOCK_VOICE_COMMAND_PHRASES = [
  'Explain quantum computing algorithms and superposition',
  'Open my project workspace and check security',
  'Analyze my code coverage and generate an engineering report',
  'Create a mission to research multi-agent architectures',
  'Show my active workforce agents',
  'What do you remember about Nova AI Operating System?',
  'Turn on my bedroom lights and check IoT nodes',
  'Read my latest system notifications and alerts',
  'Help me plan my software deployment pipeline',
];

export const MOCK_VOICE_RESPONSES: Record<string, string> = {
  quantum:
    'Quantum computing processes information using qubits in superposition states, executing matrix transformations exponentially faster than binary transistors.',
  open: 'Visual Studio Code project workspace launched successfully in path C:/Projects/Nova-AI.',
  analyze: 'Completed monorepo code coverage audit. 13 specialized engineering divisions compiled with 0 backend errors.',
  mission: 'Created autonomous DAG mission msn_voice_research_01. Solution Architect and DevOps lead assigned.',
  agents: 'Displaying 67 active workforce agents across 9 divisions.',
  lights: 'Permission approval required: Control Smart Home Lighting Node on local subnet 192.168.1.250.',
  default:
    'Nova voice engine processed your speech input cleanly. Intelligence runtime is ready for further commands.',
};
