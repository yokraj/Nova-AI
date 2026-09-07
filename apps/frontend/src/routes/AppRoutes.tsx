import React, { Suspense, lazy } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import AppLayout from '@/layouts/AppLayout';
import DashboardPage from '@/pages/DashboardPage';
import { Loader2 } from 'lucide-react';

// Route Code Splitting with React.lazy
const ChatPage = lazy(() => import('@/pages/ChatPage'));
const MemoryPage = lazy(() => import('@/pages/MemoryPage'));
const KnowledgePage = lazy(() => import('@/pages/KnowledgePage'));
const RepositoriesPage = lazy(() => import('@/pages/RepositoriesPage'));
const AgentsPage = lazy(() => import('@/pages/AgentsPage'));
const MissionControlPage = lazy(() => import('@/pages/MissionControlPage'));
const SkillsPage = lazy(() => import('@/pages/SkillsPage'));
const WorkflowsPage = lazy(() => import('@/pages/WorkflowsPage'));
const AutomationPage = lazy(() => import('@/pages/AutomationPage'));
const ComputerControlPage = lazy(() => import('@/pages/ComputerControlPage'));
const AnalyticsPage = lazy(() => import('@/pages/AnalyticsPage'));
const ModelsPage = lazy(() => import('@/pages/ModelsPage'));
const TerminalPage = lazy(() => import('@/pages/TerminalPage'));
const VoicePage = lazy(() => import('@/pages/VoicePage'));
const DeviceControlPage = lazy(() => import('@/pages/DeviceControlPage'));
const SettingsPage = lazy(() => import('@/pages/SettingsPage'));
const DesignSystemPage = lazy(() => import('@/pages/DesignSystemPage'));

const PageFallback: React.FC = () => (
  <div className="h-96 w-full flex flex-col items-center justify-center space-y-3 text-cyan-400 font-mono">
    <Loader2 className="w-8 h-8 animate-spin" />
    <span className="text-xs uppercase tracking-wider">Loading Nova Subsystem Module...</span>
  </div>
);

export const AppRoutes: React.FC = () => {
  return (
    <Routes>
      <Route path="/" element={<AppLayout />}>
        <Route index element={<DashboardPage />} />
        <Route
          path="chat"
          element={
            <Suspense fallback={<PageFallback />}>
              <ChatPage />
            </Suspense>
          }
        />
        <Route
          path="memory"
          element={
            <Suspense fallback={<PageFallback />}>
              <MemoryPage />
            </Suspense>
          }
        />
        <Route
          path="knowledge"
          element={
            <Suspense fallback={<PageFallback />}>
              <KnowledgePage />
            </Suspense>
          }
        />
        <Route
          path="repositories"
          element={
            <Suspense fallback={<PageFallback />}>
              <RepositoriesPage />
            </Suspense>
          }
        />
        <Route
          path="agents"
          element={
            <Suspense fallback={<PageFallback />}>
              <AgentsPage />
            </Suspense>
          }
        />
        <Route
          path="mission-control"
          element={
            <Suspense fallback={<PageFallback />}>
              <MissionControlPage />
            </Suspense>
          }
        />
        <Route
          path="skills"
          element={
            <Suspense fallback={<PageFallback />}>
              <SkillsPage />
            </Suspense>
          }
        />
        <Route
          path="workflows"
          element={
            <Suspense fallback={<PageFallback />}>
              <WorkflowsPage />
            </Suspense>
          }
        />
        <Route
          path="automation"
          element={
            <Suspense fallback={<PageFallback />}>
              <AutomationPage />
            </Suspense>
          }
        />
        <Route
          path="computer-control"
          element={
            <Suspense fallback={<PageFallback />}>
              <ComputerControlPage />
            </Suspense>
          }
        />
        <Route
          path="analytics"
          element={
            <Suspense fallback={<PageFallback />}>
              <AnalyticsPage />
            </Suspense>
          }
        />
        <Route
          path="models"
          element={
            <Suspense fallback={<PageFallback />}>
              <ModelsPage />
            </Suspense>
          }
        />
        <Route
          path="terminal"
          element={
            <Suspense fallback={<PageFallback />}>
              <TerminalPage />
            </Suspense>
          }
        />
        <Route
          path="voice"
          element={
            <Suspense fallback={<PageFallback />}>
              <VoicePage />
            </Suspense>
          }
        />
        <Route
          path="devices"
          element={
            <Suspense fallback={<PageFallback />}>
              <DeviceControlPage />
            </Suspense>
          }
        />
        <Route
          path="settings"
          element={
            <Suspense fallback={<PageFallback />}>
              <SettingsPage />
            </Suspense>
          }
        />
        <Route
          path="design-system"
          element={
            <Suspense fallback={<PageFallback />}>
              <DesignSystemPage />
            </Suspense>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
};

export default AppRoutes;
