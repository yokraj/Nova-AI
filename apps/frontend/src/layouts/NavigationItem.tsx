import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { LucideIcon } from 'lucide-react';
import { cn } from '@/utils/cn';

interface NavigationItemProps {
  to: string;
  icon: LucideIcon;
  label: string;
  badge?: string | number;
  collapsed?: boolean;
}

export const NavigationItem: React.FC<NavigationItemProps> = ({
  to,
  icon: Icon,
  label,
  badge,
  collapsed = false,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className="relative flex items-center"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <NavLink
        to={to}
        className={({ isActive }) =>
          cn(
            'w-full flex items-center space-x-3 px-3 py-2 rounded-xl text-xs sm:text-sm font-medium transition-all duration-200 group relative select-none',
            'focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-1 focus:ring-offset-black',
            isActive
              ? 'bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-[0_0_15px_rgba(0,240,255,0.15)] font-semibold'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 hover:border-slate-700/50 border border-transparent'
          )
        }
        aria-label={label}
      >
        {({ isActive }) => (
          <>
            <Icon
              className={cn(
                'w-4 h-4 sm:w-5 sm:h-5 transition-transform duration-200 group-hover:scale-110 shrink-0',
                isActive ? 'text-cyan-400' : 'text-slate-400 group-hover:text-cyan-300'
              )}
            />

            {!collapsed && <span className="truncate">{label}</span>}

            {!collapsed && badge !== undefined && (
              <span className="ml-auto text-[10px] font-bold font-mono px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 shrink-0">
                {badge}
              </span>
            )}

            {isActive && (
              <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-5 bg-cyan-400 rounded-r-full shadow-[0_0_8px_rgba(0,240,255,0.8)]" />
            )}
          </>
        )}
      </NavLink>

      {/* Floating Tooltip when Sidebar is Collapsed */}
      {collapsed && isHovered && (
        <div className="absolute left-full ml-3 px-2.5 py-1.5 rounded-xl bg-slate-900 border border-cyan-500/30 text-slate-100 text-xs font-medium font-sans whitespace-nowrap shadow-2xl z-50 pointer-events-none flex items-center space-x-2">
          <span>{label}</span>
          {badge !== undefined && (
            <span className="text-[10px] font-bold font-mono px-1.5 py-0.2 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-500/30">
              {badge}
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default NavigationItem;
