import { useState } from 'react';
import { BrowserOrchestrator } from '../orchestrator/browserOrchestrator';
import { BrowserResult } from '../types/browserResult';
import { BrowserActionType } from '../types/browserAction';

export function useBrowserControl() {
  const [orchestrator] = useState(() => new BrowserOrchestrator());
  const [lastResult, setLastResult] = useState<BrowserResult | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);

  const executeBrowserCommand = async (
    commandText: string,
    action: BrowserActionType,
    rawTarget: string,
    parameters?: any
  ): Promise<BrowserResult> => {
    setIsExecuting(true);
    try {
      const res = await orchestrator.processBrowserCommand(commandText, action, rawTarget, parameters);
      setLastResult(res);
      return res;
    } finally {
      setIsExecuting(false);
    }
  };

  return {
    executeBrowserCommand,
    lastResult,
    isExecuting,
  };
}
