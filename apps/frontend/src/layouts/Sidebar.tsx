import React from 'react';
import { motion } from 'framer-motion';
import {
  ChevronLeft,
  ChevronRight,
  Sparkles,
  MessageSquare,
  Rocket,
  Bot,
  Zap,
  Layers,
  Brain,
  BookOpen,
  FolderGit2,
  Globe,
  Monitor,
  Terminal,
  Clock,
  Cpu,
  BarChart3,
  Settings,
} from 'lucide-react';
import { NavigationItem } from './NavigationItem';
import { SidebarSection } from './SidebarSection';

interface SidebarProps {
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggleCollapse }) => {
  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 240 }}
      transition={{ duration: 0.2, ease: 'easeInOut' }}
      className="h-[calc(100vh-4rem)] border-r border-zinc-800/80 bg-black/95 backdrop-blur-2xl flex flex-col justify-between z-20 select-none flex-shrink-0 min-w-0"
    >
      {/* Upper Content */}
      <div className="p-2.5 space-y-3 overflow-y-auto no-scrollbar">
        {/* CORE */}
        <SidebarSection title="CORE" collapsed={collapsed} defaultExpanded={true}>
          <NavigationItem to="/" icon={Sparkles} label="Nova Core" collapsed={collapsed} />
          <NavigationItem to="/chat" icon={MessageSquare} label="Intelligence Chat" badge="Live" collapsed={collapsed} />
        </SidebarSection>

        {/* WORK */}
        <SidebarSection title="WORK" collapsed={collapsed} defaultExpanded={true}>
          <NavigationItem to="/mission-control" icon={Rocket} label="Missions" collapsed={collapsed} />
          <NavigationItem to="/agents" icon={Bot} label="Agents" collapsed={collapsed} />
          <NavigationItem to="/skills" icon={Zap} label="Learned Skills" collapsed={collapsed} />
          <NavigationItem to="/workflows" icon={Layers} label="Workflows" collapsed={collapsed} />
        </SidebarSection>

        {/* KNOWLEDGE */}
        <SidebarSection title="KNOWLEDGE" collapsed={collapsed} defaultExpanded={true}>
          <NavigationItem to="/memory" icon={Brain} label="Memory" collapsed={collapsed} />
          <NavigationItem to="/knowledge" icon={BookOpen} label="Knowledge" collapsed={collapsed} />
          <NavigationItem to="/repositories" icon={FolderGit2} label="Repositories" collapsed={collapsed} />
        </SidebarSection>

        {/* CONTROL */}
        <SidebarSection title="CONTROL" collapsed={collapsed} defaultExpanded={false}>
          <NavigationItem to="/devices" icon={Globe} label="Browser Automation" collapsed={collapsed} />
          <NavigationItem to="/computer-control" icon={Monitor} label="Computer Control" collapsed={collapsed} />
          <NavigationItem to="/terminal" icon={Terminal} label="System Control" collapsed={collapsed} />
        </SidebarSection>

        {/* AUTOMATION */}
        <SidebarSection title="AUTOMATION" collapsed={collapsed} defaultExpanded={false}>
          <NavigationItem to="/automation" icon={Clock} label="Background Tasks" collapsed={collapsed} />
        </SidebarSection>

        {/* SYSTEM */}
        <SidebarSection title="SYSTEM" collapsed={collapsed} defaultExpanded={false}>
          <NavigationItem to="/models" icon={Cpu} label="Local Models" collapsed={collapsed} />
          <NavigationItem to="/analytics" icon={BarChart3} label="Diagnostics" collapsed={collapsed} />
          <NavigationItem to="/settings" icon={Settings} label="Settings" collapsed={collapsed} />
        </SidebarSection>
      </div>

      {/* Footer Collapse Button */}
      <div className="p-2 border-t border-zinc-800/80">
        <button
          onClick={onToggleCollapse}
          className="w-full flex items-center justify-center p-2 rounded-xl bg-zinc-900/90 hover:bg-zinc-800 text-slate-400 hover:text-cyan-300 border border-zinc-800 transition-colors cursor-pointer"
          title={collapsed ? 'Expand Navigation Sidebar' : 'Collapse Navigation Sidebar'}
        >
          {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
