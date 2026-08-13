import { useState } from 'react';
import { VisionOrchestrator } from '../orchestrator/visionOrchestrator';
import { VisionResult } from '../types/visionResult';
import { VisionActionType } from '../types/visionAction';

export function useVisionControl() {
  const [orchestrator] = useState(() => new VisionOrchestrator());
  const [lastResult, setLastResult] = useState<VisionResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const executeVisionCommand = async (
    commandText: string,
    action: VisionActionType,
    targetDescription?: string,
    parameters?: any
  ): Promise<VisionResult> => {
    setIsAnalyzing(true);
    try {
      const res = await orchestrator.processVisionCommand(commandText, action, targetDescription, parameters);
      setLastResult(res);
      return res;
    } finally {
      setIsAnalyzing(false);
    }
  };

  return {
    executeVisionCommand,
    lastResult,
    isAnalyzing,
  };
}
