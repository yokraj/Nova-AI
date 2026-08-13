import React, { useState } from 'react';
import {
  Sparkles,
  Zap,
  Bot,
  Activity,
  CheckCircle2,
  Shield,
  Layers,
  Search,
} from 'lucide-react';
import { PrimaryButton, SecondaryButton, GhostButton, DangerButton, IconButton } from '@/components/ui/Buttons';
import { GlassCard, CyberCard, MetricCard, StatusCard, AgentCard, PanelCard } from '@/components/cards/Cards';
import { Panel, Section, Widget, Window } from '@/components/layout/Containers';
import { Title, Subtitle, SectionTitle, BodyText, Label, MetricValue, StatBlock, DataLabel, CodeBlock } from '@/components/display/TypographyAndDisplay';
import { StatusBadge, HealthIndicator, OnlineIndicator, ProgressBar, ProgressRing, CircularGauge } from '@/components/status/StatusIndicators';
import { Spinner, PulseLoader, Skeleton, Toast, Alert, Banner, TimelineItem } from '@/components/feedback/FeedbackAndLoaders';
import { Input, SearchInput, CommandInput, Textarea, Select, Checkbox, Switch, Slider } from '@/components/forms/FormControls';
import { UserAvatar, AgentAvatar, WorkspaceAvatar, CyberDivider, TabBar, Tab, Breadcrumb } from '@/components/navigation/NavigationAndAvatars';
import { Modal, ConfirmationDialog } from '@/components/dialogs/Dialogs';
import { Tooltip, Popover } from '@/components/tooltips/TooltipsAndPopovers';
import { MiniAreaChart, PlaceholderChart } from '@/components/charts/Charts';

export const DesignSystemPage: React.FC = () => {
  const [modalOpen, setModalOpen] = useState(false);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [switchVal, setSwitchVal] = useState(true);
  const [sliderVal, setSliderVal] = useState(75);
  const [activeTab, setActiveTab] = useState('Overview');

  return (
    <div className="space-y-10 pb-16">
      {/* Header */}
      <div className="glass-panel-cyan p-6 rounded-2xl flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-cyan-500/10 rounded-xl text-cyan-400 border border-cyan-500/30 shadow-[0_0_15px_rgba(0,240,255,0.3)]">
            <Sparkles className="w-8 h-8" />
          </div>
          <div>
            <Title>Design System & Component Catalog</Title>
            <Subtitle>Futuristic Cyber Glassmorphism Component Library for Nova AI OS</Subtitle>
          </div>
        </div>
        <StatusBadge label="PRODUCTION READY" variant="cyan" />
      </div>

      {/* Category 1: Buttons */}
      <Section title="1. Action Buttons">
        <div className="flex flex-wrap gap-4 items-center">
          <PrimaryButton icon={Zap}>Primary Execution</PrimaryButton>
          <SecondaryButton icon={Layers}>Secondary Action</SecondaryButton>
          <GhostButton icon={Activity}>Ghost Action</GhostButton>
          <DangerButton icon={Shield}>Danger Action</DangerButton>
          <IconButton icon={Bot} />
        </div>
      </Section>

      <CyberDivider />

      {/* Category 2: Cards */}
      <Section title="2. Cards & Panels">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <GlassCard>
            <Label>Glass Card Container</Label>
            <BodyText className="mt-2">Standard glassmorphic elevation card for content encapsulation.</BodyText>
          </GlassCard>
          <CyberCard>
            <Label className="text-cyan-300">Cyber Card Container</Label>
            <BodyText className="mt-2">High-priority cyan glow card with geometric background accents.</BodyText>
          </CyberCard>
          <MetricCard title="Gateway Throughput" value="85.4 req/s" change="+12.4% optimization" icon={Zap} />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
          <StatusCard title="Inference Gateway Engine" status="HEALTHY" subtitle="Ollama / vLLM local cluster" type="success" />
          <AgentCard name="Architect Agent" role="System Architecture & Design" status="active" tasksCompleted={142} avatar="A" />
        </div>
      </Section>

      <CyberDivider />

      {/* Category 3: Typography & Display */}
      <Section title="3. Typography & Data Displays">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Panel title="Metric Values & Stat Blocks">
            <MetricValue value="14.2 ms" label="Average Gateway TTFT Latency" />
            <div className="grid grid-cols-2 gap-3 mt-4">
              <StatBlock label="Vector Memory" value="142,850" subvalue="FAISS HNSW Index" />
              <StatBlock label="Active Models" value="8" subvalue="Ollama + Cloud" />
            </div>
          </Panel>
          <Panel title="Code & Structured Labels">
            <DataLabel label="Workspace" value="Nova OS" />
            <DataLabel label="Execution Engine" value="Universal Intelligence Gateway" />
            <CodeBlock code={`const engine = new InferenceGateway({\n  model: "llama3.2",\n  provider: "ollama"\n});`} />
          </Panel>
        </div>
      </Section>

      <CyberDivider />

      {/* Category 4: Status Indicators & Gauges */}
      <Section title="4. Status Indicators & Gauges">
        <div className="glass-panel p-6 rounded-2xl grid grid-cols-1 md:grid-cols-4 gap-6 items-center">
          <div className="space-y-2">
            <Label>Badges</Label>
            <div className="flex flex-wrap gap-2">
              <StatusBadge label="SUCCESS" variant="success" />
              <StatusBadge label="WARNING" variant="warning" />
              <StatusBadge label="CRITICAL" variant="danger" />
            </div>
          </div>
          <div className="space-y-2">
            <Label>Indicators</Label>
            <OnlineIndicator />
            <HealthIndicator status="healthy" />
          </div>
          <div className="space-y-2">
            <Label>Progress Bar</Label>
            <ProgressBar progress={78} />
          </div>
          <div className="flex space-x-4 items-center">
            <ProgressRing progress={85} />
            <CircularGauge value={64} label="GPU VRAM" />
          </div>
        </div>
      </Section>

      <CyberDivider />

      {/* Category 5: Feedback & Loaders */}
      <Section title="5. Feedback & Loaders">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Panel title="Alerts & Banners">
            <Alert title="System Memory Synchronized" type="success">
              All 142,850 vector memories successfully loaded into FAISS vector cache.
            </Alert>
            <Banner title="Nova AI OS Version 1.0 Online" subtitle="Universal Intelligence Inference Gateway Ready" />
          </Panel>
          <Panel title="Loaders & Timelines">
            <div className="flex space-x-6 items-center">
              <Spinner />
              <PulseLoader />
              <Skeleton className="w-32 h-6" />
            </div>
            <div className="mt-4">
              <TimelineItem title="Phase F1.3 Completed" timestamp="14:20:00" description="Enterprise Design System & Component Library built." isLast />
            </div>
          </Panel>
        </div>
      </Section>

      <CyberDivider />

      {/* Category 6: Form Controls */}
      <Section title="6. Form Controls">
        <div className="glass-panel p-6 rounded-2xl grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <Input label="Workspace Name" placeholder="e.g. Nova OS" />
            <SearchInput placeholder="Search system logs..." />
            <CommandInput placeholder="Execute command..." />
          </div>
          <div className="space-y-4">
            <Select label="Provider Selection" options={[{ value: 'ollama', label: 'Ollama Local' }, { value: 'openai', label: 'OpenAI Cloud' }]} />
            <Switch label="Enable Local GPU Acceleration" checked={switchVal} onChange={setSwitchVal} />
            <Slider label="Context Token Budget" value={sliderVal} onChange={setSliderVal} />
          </div>
        </div>
      </Section>

      <CyberDivider />

      {/* Category 7: Navigation & Dialog Trigger */}
      <Section title="7. Navigation, Dialogs & Tooltips">
        <div className="glass-panel p-6 rounded-2xl space-y-4">
          <div className="flex items-center space-x-4">
            <UserAvatar name="Admin" />
            <AgentAvatar name="Architect" />
            <WorkspaceAvatar name="Nova" />
            <Breadcrumb items={['System', 'Inference', 'Catalog']} />
          </div>
          <TabBar>
            {['Overview', 'Metrics', 'Logs'].map((tab) => (
              <Tab key={tab} label={tab} active={activeTab === tab} onClick={() => setActiveTab(tab)} />
            ))}
          </TabBar>
          <div className="flex space-x-4 pt-2">
            <Tooltip content="Execute System Modal">
              <PrimaryButton onClick={() => setModalOpen(true)}>Open Modal</PrimaryButton>
            </Tooltip>
            <SecondaryButton onClick={() => setConfirmOpen(true)}>Open Confirmation</SecondaryButton>
          </div>
        </div>
      </Section>

      <CyberDivider />

      {/* Category 8: Charts */}
      <Section title="8. Telemetry Visualization Charts">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <PlaceholderChart title="Real-Time Gateway Throughput (Req/Sec)" />
          <PlaceholderChart title="TTFT Latency Distribution (ms)" />
        </div>
      </Section>

      {/* Modals for Interactive Demo */}
      <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Enterprise Modal System">
        <BodyText>
          Modal dialog container styled with Cyber Cyan glassmorphism and backdrop blur.
        </BodyText>
        <div className="flex justify-end pt-4">
          <PrimaryButton onClick={() => setModalOpen(false)}>Close Modal</PrimaryButton>
        </div>
      </Modal>

      <ConfirmationDialog
        isOpen={confirmOpen}
        onClose={() => setConfirmOpen(false)}
        onConfirm={() => console.log('Confirmed')}
        title="Confirm System Execution"
        message="Are you sure you want to trigger this enterprise operation?"
      />
    </div>
  );
};

export default DesignSystemPage;
