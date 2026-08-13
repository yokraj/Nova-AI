import React, { useState } from 'react';
import { Copy, RefreshCw, ThumbsUp, ThumbsDown, Volume2, Check } from 'lucide-react';
import { cn } from '@/utils/cn';

interface ResponseToolbarProps {
  onCopy: () => void;
  onRegenerate?: () => void;
  className?: string;
}

export const ResponseToolbar: React.FC<ResponseToolbarProps> = ({
  onCopy,
  onRegenerate,
  className,
}) => {
  const [copied, setCopied] = useState(false);
  const [liked, setLiked] = useState<boolean | null>(null);

  const handleCopyClick = () => {
    onCopy();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={cn('flex items-center space-x-1.5 pt-2 text-slate-400 text-xs font-mono', className)}>
      <button
        onClick={handleCopyClick}
        className="p-1.5 rounded-lg hover:bg-slate-800 hover:text-cyan-300 transition-all cursor-pointer flex items-center space-x-1"
        title="Copy response"
      >
        {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
        <span className="text-[11px]">{copied ? 'Copied' : 'Copy'}</span>
      </button>

      {onRegenerate && (
        <button
          onClick={onRegenerate}
          className="p-1.5 rounded-lg hover:bg-slate-800 hover:text-cyan-300 transition-all cursor-pointer flex items-center space-x-1"
          title="Regenerate response"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span className="text-[11px]">Regenerate</span>
        </button>
      )}

      <button
        onClick={() => setLiked(liked === true ? null : true)}
        className={cn('p-1.5 rounded-lg hover:bg-slate-800 transition-all cursor-pointer', liked === true && 'text-emerald-400 bg-emerald-500/10')}
        title="Good response"
      >
        <ThumbsUp className="w-3.5 h-3.5" />
      </button>

      <button
        onClick={() => setLiked(liked === false ? null : false)}
        className={cn('p-1.5 rounded-lg hover:bg-slate-800 transition-all cursor-pointer', liked === false && 'text-rose-400 bg-rose-500/10')}
        title="Poor response"
      >
        <ThumbsDown className="w-3.5 h-3.5" />
      </button>

      <button
        onClick={() => alert('[TTS Voice Synth] Reading aloud response...')}
        className="p-1.5 rounded-lg hover:bg-slate-800 hover:text-purple-300 transition-all cursor-pointer"
        title="Read aloud (Voice Synth)"
      >
        <Volume2 className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};

export default ResponseToolbar;
