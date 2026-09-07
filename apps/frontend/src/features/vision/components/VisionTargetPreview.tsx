import React from 'react';
import { Eye, Crosshair } from 'lucide-react';
import { VisionTarget } from '../types/visionTarget';

interface VisionTargetPreviewProps {
  target: VisionTarget | null;
  resolution?: { width: number; height: number };
  activeApp?: string;
  activeTitle?: string;
  onApproveAction?: () => void;
}

export const VisionTargetPreview: React.FC<VisionTargetPreviewProps> = ({
  target,
  resolution = { width: 1920, height: 1080 },
  activeApp = 'Windows Desktop',
  activeTitle = 'Workspace',
  onApproveAction,
}) => {
  if (!target) return null;

  const confidencePercent = Math.round(target.confidence * 100);
  let statusBadge = 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
  let statusLabel = 'HIGH CONFIDENCE (SAFE)';

  if (target.confidence < 0.75) {
    statusBadge = 'bg-rose-500/20 text-rose-400 border-rose-500/30';
    statusLabel = 'LOW CONFIDENCE (BLOCKED)';
  } else if (target.confidence < 0.90) {
    statusBadge = 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    statusLabel = 'MEDIUM CONFIDENCE (VERIFY)';
  }

  const bbox = target.boundingBox || { x: 0, y: 0, width: 0, height: 0 };
  const centerX = Math.round(bbox.x + bbox.width / 2);
  const centerY = Math.round(bbox.y + bbox.height / 2);

  return (
    <div className="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 space-y-3 font-sans shadow-xl">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Eye className="w-4 h-4 text-cyan-400" />
          <span className="text-xs font-bold text-slate-200">Vision Grounding Preview</span>
        </div>
        <span className={`px-2 py-0.5 rounded-full text-[10px] font-mono border ${statusBadge}`}>
          {statusLabel} ({confidencePercent}%)
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs font-mono bg-slate-950 p-3 rounded-xl border border-slate-800/80">
        <div>
          <span className="text-slate-500">Target Label:</span>{' '}
          <span className="text-slate-100 font-bold">{target.label}</span>
        </div>
        <div>
          <span className="text-slate-500">Element Type:</span>{' '}
          <span className="text-cyan-400">{target.type}</span>
        </div>
        <div>
          <span className="text-slate-500">Center (X, Y):</span>{' '}
          <span className="text-slate-200">
            ({centerX}, {centerY})
          </span>
        </div>
        <div>
          <span className="text-slate-500">Bounds:</span>{' '}
          <span className="text-slate-200">
            {bbox.width}x{bbox.height}
          </span>
        </div>
        <div className="col-span-2 text-[11px] text-slate-400 truncate">
          <span className="text-slate-500">Window:</span> {activeApp} — {activeTitle}
        </div>
      </div>

      {target.confidence >= 0.75 && target.confidence < 0.90 && onApproveAction && (
        <button
          onClick={onApproveAction}
          className="w-full py-2 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 text-xs font-mono font-bold transition-all cursor-pointer flex items-center justify-center space-x-2"
        >
          <Crosshair className="w-3.5 h-3.5" />
          <span>Approve Visual Click at ({centerX}, {centerY})</span>
        </button>
      )}
    </div>
  );
};
