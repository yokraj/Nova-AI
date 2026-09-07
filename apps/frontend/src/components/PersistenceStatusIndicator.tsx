import React from 'react';

export type PersistenceState = 'PERSISTED' | 'SYNCING' | 'OFFLINE' | 'FAILED';

interface PersistenceStatusIndicatorProps {
  status: PersistenceState;
  className?: string;
}

export const PersistenceStatusIndicator: React.FC<PersistenceStatusIndicatorProps> = ({
  status,
  className = '',
}) => {
  let badgeColor = 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
  let label = 'PERSISTED';
  let dotColor = 'bg-emerald-400';

  if (status === 'SYNCING') {
    badgeColor = 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    label = 'SYNCING';
    dotColor = 'bg-blue-400 animate-pulse';
  } else if (status === 'OFFLINE') {
    badgeColor = 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    label = 'OFFLINE (LOCAL)';
    dotColor = 'bg-amber-400';
  } else if (status === 'FAILED') {
    badgeColor = 'bg-rose-500/20 text-rose-400 border-rose-500/30';
    label = 'FAILED TO SAVE';
    dotColor = 'bg-rose-400';
  }

  return (
    <div
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono border ${badgeColor} ${className}`}
      title={`Persistence Status: ${label}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotColor}`} />
      <span>{label}</span>
    </div>
  );
};
