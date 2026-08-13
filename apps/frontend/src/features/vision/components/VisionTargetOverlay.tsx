import React from 'react';
import { VisionTarget } from '../types/visionTarget';
import { cn } from '@/utils/cn';

interface VisionTargetOverlayProps {
  target: VisionTarget;
  className?: string;
}

export const VisionTargetOverlay: React.FC<VisionTargetOverlayProps> = ({ target, className }) => {
  if (!target.boundingBox) return null;

  return (
    <div
      className={cn('absolute border-2 border-cyan-400 bg-cyan-500/10 rounded-lg flex items-start justify-between p-1 text-[10px] font-mono text-cyan-200 shadow-lg animate-pulse', className)}
      style={{
        left: `${target.boundingBox.x}px`,
        top: `${target.boundingBox.y}px`,
        width: `${target.boundingBox.width}px`,
        height: `${target.boundingBox.height}px`,
      }}
    >
      <span className="bg-slate-950/90 px-1.5 py-0.5 rounded border border-cyan-400 font-bold">
        {target.label} ({(target.confidence * 100).toFixed(0)}%)
      </span>
    </div>
  );
};

export default VisionTargetOverlay;
