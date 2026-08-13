import { IntentClassification } from './intent';
import { ResolvedCapability } from './capability';
import { CommandPermissionAssessment } from './permission';
import { CommandExecutionState, CommandPlan } from './execution';
import { CommandResult } from './commandResult';

export type CommandSource = 'TEXT' | 'VOICE' | 'VISION' | 'FILE' | 'SYSTEM';

export interface UniversalCommand {
  id: string;
  source: CommandSource;
  rawInput: string;
  timestamp: string;
  intent?: IntentClassification;
  target?: string;
  context?: Record<string, any>;
  capability?: ResolvedCapability;
  permission?: CommandPermissionAssessment;
  plan?: CommandPlan;
  executionState: CommandExecutionState;
  result?: CommandResult;
}
