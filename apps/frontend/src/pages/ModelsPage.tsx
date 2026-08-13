import React, { useState, useEffect } from 'react';
import { Cpu, Server, CheckCircle2, AlertCircle, RefreshCw, Sliders, ShieldCheck, Zap } from 'lucide-react';
import { ModelConfigStore, ModelConfig } from '@/features/ai-runtime/config/modelConfigStore';
import { LocalModelProvider } from '@/features/ai-runtime/providers/localModelProvider';

export const ModelsPage: React.FC = () => {
  const [config, setConfig] = useState<ModelConfig>(() => ModelConfigStore.getConfig());
  const [isConnected, setIsConnected] = useState<boolean | null>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [testMessage, setTestMessage] = useState<string>('');

  const checkConnection = async () => {
    setIsTesting(true);
    setTestMessage('Testing local LLM endpoint...');
    const provider = new LocalModelProvider();
    const online = await provider.isAvailable();
    setIsConnected(online);
    setIsTesting(false);
    if (online) {
      setTestMessage(`Successfully connected to ${config.baseUrl} (${config.model})`);
    } else {
      setTestMessage(`Could not connect to ${config.baseUrl}. Falling back to Mock Engine.`);
    }
  };

  useEffect(() => {
    checkConnection();
  }, [config.baseUrl]);

  const handleChange = (field: keyof ModelConfig, value: any) => {
    const updated = ModelConfigStore.updateConfig({ [field]: value });
    setConfig(updated);
  };

  return (
    <div className="space-y-6 font-sans text-slate-100 max-w-5xl mx-auto p-4">
      {/* Header */}
      <div className="glass-panel-cyan p-6 rounded-3xl flex items-center justify-between border border-cyan-500/30 bg-slate-950/80 backdrop-blur-xl shadow-2xl">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-cyan-500/10 rounded-2xl text-cyan-400 border border-cyan-500/30">
            <Cpu className="w-8 h-8" />
          </div>
          <div>
            <h1 className="text-2xl font-bold tracking-wide text-slate-100">Inference Gateway & Local AI Brain</h1>
            <p className="text-sm text-slate-400">
              Configure local Ollama / OpenAI-compatible model endpoints for autonomous agent reasoning
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-full border text-xs font-mono font-bold uppercase ${
              isConnected
                ? 'bg-emerald-500/10 text-emerald-300 border-emerald-500/40'
                : 'bg-amber-500/10 text-amber-300 border-amber-500/40'
            }`}
          >
            {isConnected ? (
              <>
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                <span>LOCAL MODEL CONNECTED</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-4 h-4 text-amber-400" />
                <span>LOCAL MODEL UNAVAILABLE — MOCK FALLBACK</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Connection & Configuration Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 p-6 rounded-3xl border border-slate-800 bg-slate-950/80 backdrop-blur-xl shadow-xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2 font-mono text-cyan-300 font-bold text-sm">
              <Server className="w-4 h-4 text-cyan-400" />
              <span>LOCAL MODEL PROVIDER SETTINGS</span>
            </div>
            <button
              onClick={checkConnection}
              disabled={isTesting}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 hover:bg-cyan-500/30 text-xs font-mono transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isTesting ? 'animate-spin' : ''}`} />
              <span>Test Connection</span>
            </button>
          </div>

          {testMessage && (
            <div className={`p-3 rounded-2xl border font-mono text-xs ${isConnected ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-200' : 'bg-amber-500/10 border-amber-500/30 text-amber-200'}`}>
              {testMessage}
            </div>
          )}

          <div className="space-y-4 text-sm font-sans">
            <div>
              <label className="block text-xs font-mono text-slate-400 mb-1.5 uppercase">
                Base URL (Ollama / OpenAI-compatible endpoint)
              </label>
              <input
                type="text"
                value={config.baseUrl}
                onChange={(e) => handleChange('baseUrl', e.target.value)}
                placeholder="http://127.0.0.1:11434/v1"
                className="w-full px-4 py-2.5 rounded-2xl bg-slate-900 border border-slate-800 text-slate-100 font-mono text-xs focus:outline-none focus:border-cyan-500"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-mono text-slate-400 mb-1.5 uppercase">
                  Model Identifier
                </label>
                <input
                  type="text"
                  value={config.model}
                  onChange={(e) => handleChange('model', e.target.value)}
                  placeholder="llama3.2"
                  className="w-full px-4 py-2.5 rounded-2xl bg-slate-900 border border-slate-800 text-slate-100 font-mono text-xs focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <label className="block text-xs font-mono text-slate-400 mb-1.5 uppercase">
                  Timeout (ms)
                </label>
                <input
                  type="number"
                  value={config.timeoutMs}
                  onChange={(e) => handleChange('timeoutMs', Number(e.target.value))}
                  className="w-full px-4 py-2.5 rounded-2xl bg-slate-900 border border-slate-800 text-slate-100 font-mono text-xs focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-mono text-slate-400 mb-1.5 uppercase">
                  Temperature ({config.temperature})
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={config.temperature}
                  onChange={(e) => handleChange('temperature', Number(e.target.value))}
                  className="w-full accent-cyan-400"
                />
              </div>
              <div>
                <label className="block text-xs font-mono text-slate-400 mb-1.5 uppercase">
                  Max Tokens
                </label>
                <input
                  type="number"
                  value={config.maxTokens}
                  onChange={(e) => handleChange('maxTokens', Number(e.target.value))}
                  className="w-full px-4 py-2.5 rounded-2xl bg-slate-900 border border-slate-800 text-slate-100 font-mono text-xs focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Status & Security Constraints Card */}
        <div className="p-6 rounded-3xl border border-slate-800 bg-slate-950/80 backdrop-blur-xl shadow-xl space-y-4">
          <div className="flex items-center space-x-2 font-mono text-cyan-300 font-bold text-sm border-b border-slate-800 pb-3">
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
            <span>AI SAFETY & RUNTIME BOUNDS</span>
          </div>

          <div className="space-y-3 font-mono text-xs text-slate-300">
            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-slate-400">Strict Tool Whitelist:</span>
              <span className="text-emerald-400 font-bold">ENFORCED</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-slate-400">Shell Code Execution:</span>
              <span className="text-rose-400 font-bold">FORBIDDEN</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-slate-400">Prompt Injection Guard:</span>
              <span className="text-emerald-400 font-bold">ACTIVE</span>
            </div>
            <div className="flex items-center justify-between p-2 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-slate-400">Execution Step Budget:</span>
              <span className="text-cyan-400 font-bold">30 STEPS MAX</span>
            </div>
          </div>

          <div className="pt-2 text-[11px] text-slate-400 leading-relaxed font-sans">
            Nova uses structured LLM planning. The AI model proposes tool calls, while the Native Execution Runtime validates permissions, security policies, and verified state changes.
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModelsPage;
