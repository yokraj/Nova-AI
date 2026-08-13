import React, { useState } from 'react';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { cn } from '@/utils/cn';

interface SidebarSectionProps {
  title: string;
  children: React.ReactNode;
  defaultExpanded?: boolean;
  collapsed?: boolean;
}

export const SidebarSection: React.FC<SidebarSectionProps> = ({
  title,
  children,
  defaultExpanded = true,
  collapsed = false,
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  if (collapsed) {
    return <div className="space-y-1.5 py-1">{children}</div>;
  }

  return (
    <div className="space-y-1 py-1.5">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between px-3 py-1 text-[11px] font-bold font-mono tracking-wider uppercase text-slate-400 hover:text-slate-200 transition-colors"
      >
        <span>{title}</span>
        {isExpanded ? (
          <ChevronDown className="w-3.5 h-3.5" />
        ) : (
          <ChevronRight className="w-3.5 h-3.5" />
        )}
      </button>
      {isExpanded && <div className="space-y-1 pl-1">{children}</div>}
    </div>
  );
};

export default SidebarSection;
