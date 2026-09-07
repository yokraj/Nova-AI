import React, { useState } from 'react';
import TopNavigation from './TopNavigation';
import Sidebar from './Sidebar';
import MainWorkspace from './MainWorkspace';
import RightPanel from './RightPanel';
import StatusBar from './StatusBar';

export const AppLayout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [rightPanelOpen, setRightPanelOpen] = useState<boolean>(false);

  return (
    <div className="min-h-screen max-h-screen w-full flex flex-col bg-black text-slate-100 overflow-hidden font-sans">
      {/* Top Navigation Header */}
      <TopNavigation onToggleRightPanel={() => setRightPanelOpen(!rightPanelOpen)} />

      {/* Center Layout Workspace */}
      <div className="flex-1 flex min-w-0 overflow-hidden relative bg-black">
        {/* Left Sidebar */}
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Main Workspace (Outlet Page Content) */}
        <MainWorkspace />

        {/* Inspection Slide-Over Right Panel */}
        <RightPanel isOpen={rightPanelOpen} onClose={() => setRightPanelOpen(false)} />
      </div>

      {/* Bottom Status Bar */}
      <StatusBar />
    </div>
  );
};

export default AppLayout;
