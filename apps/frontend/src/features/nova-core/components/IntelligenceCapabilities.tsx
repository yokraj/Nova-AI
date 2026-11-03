import React from 'react';
import { motion } from 'framer-motion';
import { Brain, Eye, Zap, Monitor, ArrowUpRight } from 'lucide-react';
import { cn } from '@/utils/cn';

export interface IntelligenceCapabilitiesProps {
  onSelectCapability?: (capability: 'think' | 'see' | 'do' | 'control') => void;
  className?: string;
}

export const IntelligenceCapabilities: React.FC<IntelligenceCapabilitiesProps> = ({
  onSelectCapability,
  className,
}) => {
  const capabilities = [
    {
      id: 'think' as const,
      tag: '01',
      title: 'THINK',
      subtitle: 'Reason, Plan, Solve',
      description: 'Autonomous reasoning, multi-step decomposition & arithmetic',
      icon: Brain,
      glowColor: 'group-hover:border-purple-400/60 group-hover:shadow-[0_0_20px_rgba(168,85,247,0.25)]',
      iconColor: 'text-purple-400',
      badge: 'REASONING',
    },
    {
      id: 'see' as const,
      tag: '02',
      title: 'SEE',
      subtitle: 'Understand, Analyze',
      description: 'Document intelligence, screen understanding & OCR inspection',
      icon: Eye,
      glowColor: 'group-hover:border-cyan-400/60 group-hover:shadow-[0_0_20px_rgba(0,240,255,0.25)]',
      iconColor: 'text-cyan-400',
      badge: 'VISION',
    },
    {
      id: 'do' as const,
      tag: '03',
      title: 'DO',
      subtitle: 'Automate, Execute',
      description: 'Background tasks, autonomous workflows & scheduled triggers',
      icon: Zap,
      glowColor: 'group-hover:border-amber-400/60 group-hover:shadow-[0_0_20px_rgba(255,170,0,0.25)]',
      iconColor: 'text-amber-400',
      badge: 'AUTOMATE',
    },
    {
      id: 'control' as const,
      tag: '04',
      title: 'CONTROL',
      subtitle: 'Applications, Files, Devices',
      description: 'Real desktop automation, window management & keyboard input',
      icon: Monitor,
      glowColor: 'group-hover:border-sky-400/60 group-hover:shadow-[0_0_20px_rgba(56,189,248,0.25)]',
      iconColor: 'text-sky-400',
      badge: 'NATIVE',
    },
  ];

  return (
    <div className={cn('grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 w-full select-none', className)}>
      {capabilities.map((cap) => {
        const Icon = cap.icon;
        return (
          <motion.div
            key={cap.id}
            whileHover={{ y: -3, scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => onSelectCapability?.(cap.id)}
            className={cn(
              'group relative p-2.5 sm:p-3 rounded-2xl bg-slate-950/70 backdrop-blur-xl border border-cyan-500/20 hover:bg-slate-900/80 transition-all duration-300 cursor-pointer shadow-[0_4px_25px_rgba(0,0,0,0.6)] flex flex-col justify-between overflow-hidden',
              cap.glowColor
            )}
            role="button"
            tabIndex={0}
            aria-label={`${cap.title}: ${cap.subtitle}`}
          >
            {/* Top Corner HUD Accent Brackets */}
            <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-cyan-400/60 rounded-tl" />
            <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-cyan-400/60 rounded-tr" />
            <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-cyan-400/40 rounded-bl" />
            <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-cyan-400/40 rounded-br" />

            {/* Subtle Gradient Hover Sweep */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />

            {/* Card Header: Icon + Badge + Arrow */}
            <div className="flex items-center justify-between mb-2 z-10">
              <div className="flex items-center space-x-2">
                <div className="p-2 rounded-xl bg-slate-900/90 border border-cyan-500/30 group-hover:border-cyan-400 transition-colors shadow-inner">
                  <Icon className={cn('w-4 h-4', cap.iconColor)} />
                </div>
                <span className="font-mono text-[9px] tracking-widest text-slate-500 font-bold">
                  [{cap.tag}]
                </span>
              </div>

              <div className="flex items-center space-x-1.5">
                <span className="text-[9px] font-mono tracking-wider px-1.5 py-0.5 rounded bg-slate-900 border border-slate-800 text-slate-400 group-hover:text-cyan-300 group-hover:border-cyan-500/40 transition-colors">
                  {cap.badge}
                </span>
                <ArrowUpRight className="w-3.5 h-3.5 text-slate-600 group-hover:text-cyan-400 transition-colors" />
              </div>
            </div>

            {/* Title & Subtitle */}
            <div className="space-y-0.5 z-10">
              <div className="flex items-baseline space-x-2">
                <span className="font-extrabold text-sm sm:text-base tracking-wider text-white group-hover:text-cyan-300 transition-colors">
                  {cap.title}
                </span>
                <span className="text-[11px] font-mono text-cyan-400/80 font-medium">
                  • {cap.subtitle}
                </span>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed font-sans line-clamp-2">
                {cap.description}
              </p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

export default IntelligenceCapabilities;
