import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, MicOff, Paperclip, Camera, Square, X, Terminal } from 'lucide-react';
import { cn } from '@/utils/cn';
import { PrimaryButton, IconButton } from '@/components/ui/Buttons';
import { AttachmentFile } from '../types/message';

interface ConversationComposerProps {
  onSendMessage: (prompt: string, attachments?: AttachmentFile[]) => void;
  isStreaming: boolean;
  onStopStreaming: () => void;
  className?: string;
}

export const ConversationComposer: React.FC<ConversationComposerProps> = ({
  onSendMessage,
  isStreaming,
  onStopStreaming,
  className,
}) => {
  const [prompt, setPrompt] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [attachments, setAttachments] = useState<AttachmentFile[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Keyboard shortcut Ctrl+K to focus composer
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        textareaRef.current?.focus();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSend = () => {
    if (!prompt.trim() && attachments.length === 0) return;
    onSendMessage(prompt, attachments.length > 0 ? attachments : undefined);
    setPrompt('');
    setAttachments([]);
  };

  const handleAddMockAttachment = () => {
    const mockFile: AttachmentFile = {
      id: `att_${Date.now()}`,
      name: `architecture_spec_${Math.floor(Math.random() * 100)}.pdf`,
      sizeBytes: 245000,
      type: 'pdf',
      status: 'ready',
    };
    setAttachments((prev) => [...prev, mockFile]);
  };

  const removeAttachment = (id: string) => {
    setAttachments((prev) => prev.filter((a) => a.id !== id));
  };

  const toggleMic = () => {
    setIsRecording(!isRecording);
    if (!isRecording) {
      setPrompt('Listening voice input macro...');
    } else {
      setPrompt('Explain quantum computing algorithms and quicksort benchmarks.');
    }
  };

  return (
    <div className={cn('w-full max-w-4xl mx-auto space-y-2 sticky bottom-4 z-20', className)}>
      {/* Attachment Previews */}
      {attachments.length > 0 && (
        <div className="flex items-center space-x-2 px-3 py-2 bg-slate-950/90 rounded-xl border border-slate-800 text-xs font-mono overflow-x-auto">
          <span className="text-slate-500 uppercase">Attached:</span>
          {attachments.map((att) => (
            <div key={att.id} className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-700 text-cyan-300 flex items-center space-x-1.5 shrink-0">
              <Paperclip className="w-3.5 h-3.5 text-slate-400" />
              <span>{att.name}</span>
              <button onClick={() => removeAttachment(att.id)} className="text-slate-500 hover:text-rose-400">
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Main Composer Box */}
      <div className="relative group">
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-cyan-500/20 via-purple-600/20 to-blue-600/20 blur-md opacity-50 group-hover:opacity-100 transition-opacity pointer-events-none" />
        <div className="relative bg-slate-950/95 rounded-2xl border border-slate-800 group-hover:border-cyan-500/50 transition-all p-3 shadow-2xl space-y-2">
          <div className="flex items-start space-x-2">
            <Terminal className="w-5 h-5 text-cyan-400 mt-2 shrink-0 ml-1" />
            <textarea
              ref={textareaRef}
              rows={2}
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Ask Nova anything... (Press Enter to send, Shift+Enter for newline, Ctrl+K to focus)"
              className="w-full bg-transparent text-sm text-slate-100 placeholder-slate-500 focus:outline-none py-1 px-1 font-sans resize-none"
            />
          </div>

          <div className="flex items-center justify-between border-t border-slate-800/80 pt-2 text-xs font-mono">
            <div className="flex items-center space-x-1">
              <IconButton
                icon={Paperclip}
                size="sm"
                className="text-slate-400 hover:text-cyan-300"
                title="Attach Document/File"
                onClick={handleAddMockAttachment}
              />
              <IconButton
                icon={Camera}
                size="sm"
                className="text-slate-400 hover:text-cyan-300"
                title="Attach Vision Image"
                onClick={handleAddMockAttachment}
              />
              <button
                onClick={toggleMic}
                className={cn(
                  'p-1.5 rounded-lg border text-xs transition-all cursor-pointer flex items-center space-x-1',
                  isRecording
                    ? 'bg-rose-500 text-white border-rose-400 animate-pulse'
                    : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-purple-300'
                )}
                title="Voice Input"
              >
                {isRecording ? <MicOff className="w-3.5 h-3.5" /> : <Mic className="w-3.5 h-3.5" />}
              </button>
            </div>

            <div className="flex items-center space-x-2">
              {isStreaming ? (
                <button
                  onClick={onStopStreaming}
                  className="px-3 py-1.5 rounded-xl bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 border border-rose-500/40 font-bold transition-all cursor-pointer flex items-center space-x-1.5"
                >
                  <Square className="w-3.5 h-3.5" />
                  <span>Stop Generation</span>
                </button>
              ) : (
                <PrimaryButton
                  size="sm"
                  disabled={!prompt.trim() && attachments.length === 0}
                  onClick={handleSend}
                  icon={Send}
                >
                  Send
                </PrimaryButton>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConversationComposer;
