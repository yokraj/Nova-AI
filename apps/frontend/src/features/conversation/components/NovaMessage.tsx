import React from 'react';
import { motion } from 'framer-motion';
import { Bot } from 'lucide-react';
import { cn } from '@/utils/cn';
import { ConversationMessage, ResponseBlock } from '../types/message';
import CodeBlock from './CodeBlock';
import TableBlock from './TableBlock';
import CitationsBlock from './CitationsBlock';
import ThinkingIndicator from './ThinkingIndicator';
import ResponseToolbar from './ResponseToolbar';
import ToolActivity from './ToolActivity';
import MissionActivity from './MissionActivity';
import ApprovalActivity from './ApprovalActivity';
import novaCoreImg from '@/assets/nova-core.png';

interface NovaMessageProps {
  message: ConversationMessage;
  onRegenerate?: () => void;
  onApproveAction?: (approvalId: string) => void;
  onRejectAction?: (approvalId: string) => void;
  className?: string;
}

export const NovaMessage: React.FC<NovaMessageProps> = ({
  message,
  onRegenerate,
  onApproveAction,
  onRejectAction,
  className,
}) => {
  const handleCopyMessage = () => {
    const fullText = message.blocks
      ? message.blocks.map((b) => b.content || (b.codeData ? b.codeData.code : '')).join('\n\n')
      : message.content;
    navigator.clipboard.writeText(fullText);
  };

  return (
    <div className={cn('flex items-start space-x-3 my-4', className)}>
      {/* Nova Core Mini Orb Avatar */}
      <motion.div
        animate={{ scale: message.status === 'streaming' ? [1, 1.05, 1] : 1 }}
        transition={{ duration: 1.5, repeat: message.status === 'streaming' ? Infinity : 0 }}
        className="w-9 h-9 rounded-full overflow-hidden shrink-0 border border-cyan-400 shadow-[0_0_15px_rgba(0,240,255,0.4)] mt-1"
      >
        <img src={novaCoreImg} alt="Nova Core" className="w-full h-full object-cover" />
      </motion.div>

      <div className="flex-1 max-w-3xl space-y-3">
        {/* Thinking State */}
        {message.status === 'thinking' && (
          <ThinkingIndicator stage={message.thinkingStage || 'UNDERSTANDING'} />
        )}

        {/* Message Container Bubble */}
        <div className="p-5 rounded-3xl rounded-tl-sm bg-slate-900/90 border border-cyan-500/30 text-slate-100 shadow-2xl space-y-3 font-sans text-sm leading-relaxed">
          {/* Main content text if no blocks */}
          {(!message.blocks || message.blocks.length === 0) && message.content && (
            <div>{message.content}</div>
          )}

          {/* Render Response Blocks */}
          {message.blocks &&
            message.blocks.map((block: ResponseBlock) => {
              switch (block.type) {
                case 'text':
                case 'markdown':
                  return (
                    <div key={block.id} className="space-y-2 leading-relaxed font-sans">
                      {block.content}
                    </div>
                  );

                case 'code':
                  return block.codeData ? <CodeBlock key={block.id} data={block.codeData} /> : null;

                case 'table':
                  return block.tableData ? <TableBlock key={block.id} data={block.tableData} /> : null;

                case 'citation':
                  return block.citationsData ? <CitationsBlock key={block.id} citations={block.citationsData} /> : null;

                case 'tool_activity':
                  return block.toolData ? <ToolActivity key={block.id} data={block.toolData} /> : null;

                case 'agent_activity':
                  return block.agentData ? (
                    <div key={block.id} className="p-3 rounded-2xl bg-slate-950/80 border border-cyan-500/40 text-xs font-mono space-y-2">
                      <div className="flex items-center space-x-2 text-cyan-300 font-bold">
                        <Bot className="w-4 h-4 text-cyan-400" />
                        <span>AGENT: {block.agentData.agentName} ({block.agentData.division})</span>
                      </div>
                      <div className="text-slate-300">{block.agentData.task}</div>
                    </div>
                  ) : null;

                case 'mission':
                  return block.missionData ? <MissionActivity key={block.id} data={block.missionData} /> : null;

                case 'approval':
                  return block.approvalData ? (
                    <ApprovalActivity
                      key={block.id}
                      data={block.approvalData}
                      onApprove={() => onApproveAction?.(block.approvalData!.id)}
                      onReject={() => onRejectAction?.(block.approvalData!.id)}
                    />
                  ) : null;

                default:
                  return null;
              }
            })}

          {/* Response Toolbar (Copy, Regenerate, Feedback) */}
          <ResponseToolbar
            onCopy={handleCopyMessage}
            onRegenerate={onRegenerate}
          />
        </div>
      </div>
    </div>
  );
};

export default NovaMessage;
