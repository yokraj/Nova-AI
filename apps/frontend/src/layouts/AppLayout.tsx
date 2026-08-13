import React, { useState } from 'react';
import TopNavigation from './TopNavigation';
import Sidebar from './Sidebar';
import MainWorkspace from './MainWorkspace';
import RightPanel from './RightPanel';
import StatusBar from './StatusBar';

export const AppLayout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [rightPanelOpen, setRightPanelOpen] = useState<boolean>(true);

  return (
    <div className="h-screen w-screen flex flex-col bg-slate-950 text-slate-100 overflow-hidden">
      {/* Top Navigation */}
      <TopNavigation onToggleRightPanel={() => setRightPanelOpen(!rightPanelOpen)} />

      {/* Center Layout Area */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Left Sidebar */}
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggleCollapse={() => setSidebarCollapsed(!sidebarCollapsed)}
        />

        {/* Main Workspace (Outlet Page Content) */}
        <MainWorkspace />

        {/* Right Inspection Panel */}
        <RightPanel isOpen={rightPanelOpen} onClose={() => setRightPanelOpen(false)} />
      </div>

      {/* Bottom Status Bar */}
      <StatusBar />
    </div>
  );
};

export default AppLayout;
