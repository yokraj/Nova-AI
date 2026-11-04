import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  X,
  Settings,
  Globe,
  Mic,
  Volume2,
  Sliders,
  Sparkles,
  Radio,
  Check,
  UserCheck,
  Play,
  Square,
  Loader2,
  Wifi,
  WifiOff,
  AlertCircle,
} from 'lucide-react';
import { cn } from '@/utils/cn';
import {
  VoiceSettingsConfig,
  SupportedLanguageType,
  VoiceIdentityType,
  VoiceModeType,
  InstalledSapiVoice,
  savePersistedVoiceSettings,
} from '../types/voiceSettings';
import { NOVA_VOICE_PROFILES } from '../services/webSpeechEngine';
import { BackendTTSAudioPlayer, TTSMetadataResult } from '../services/backendTTSPlayer';
import { APP_CONFIG } from '@/config/app.config';

interface VoiceSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  settings: VoiceSettingsConfig;
  onUpdateSettings: (newSettings: VoiceSettingsConfig) => void;
  installedVoices?: SpeechSynthesisVoice[];
  activeVoiceInfo?: { name: string; lang: string; isExactLocale: boolean };
  className?: string;
}

export const VoiceSettings: React.FC<VoiceSettingsProps> = ({
  isOpen,
  onClose,
  settings,
  onUpdateSettings,
  activeVoiceInfo,
  className,
}) => {
  const [activeTab, setActiveTab] = useState<'profile' | 'language' | 'speech' | 'interaction'>('profile');
  const [installedSapiVoices, setInstalledSapiVoices] = useState<InstalledSapiVoice[]>([]);
  const [isPreviewLoading, setIsPreviewLoading] = useState(false);
  const [isPreviewPlaying, setIsPreviewPlaying] = useState(false);
  const [previewMeta, setPreviewMeta] = useState<TTSMetadataResult | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);

  const previewPlayerRef = useRef<BackendTTSAudioPlayer | null>(null);

  // Initialize preview audio player
  useEffect(() => {
    if (!previewPlayerRef.current) {
      previewPlayerRef.current = new BackendTTSAudioPlayer();
    }
    return () => {
      previewPlayerRef.current?.stop();
    };
  }, []);

  // Fetch installed Windows SAPI voices dynamically from backend on modal open
  useEffect(() => {
    if (!isOpen) return;

    let isMounted = true;
    async function loadVoices() {
      try {
        const res = await fetch(`${APP_CONFIG.apiBaseUrl}/voice/sapi/voices`, {
          signal: AbortSignal.timeout(4000),
        });
        if (res.ok && isMounted) {
          const data = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            setInstalledSapiVoices(data);
          }
        }
      } catch (err) {
        // Fallback default installed voice if backend is not reachable
        if (isMounted) {
          setInstalledSapiVoices([
            {
              name: 'Microsoft Zira Desktop',
              culture: 'en-US',
              gender: 'Female',
              age: 'Adult',
              description: 'Microsoft Zira Desktop - English (United States)',
              is_female: true,
              is_default: true,
            },
            {
              name: 'Microsoft David Desktop',
              culture: 'en-US',
              gender: 'Male',
              age: 'Adult',
              description: 'Microsoft David Desktop - English (United States)',
              is_female: false,
              is_default: false,
            },
          ]);
        }
      }
    }

    loadVoices();
    return () => {
      isMounted = false;
      previewPlayerRef.current?.stop();
      setIsPreviewPlaying(false);
      setIsPreviewLoading(false);
    };
  }, [isOpen]);

  if (!isOpen) return null;

  const handleUpdate = (partial: Partial<VoiceSettingsConfig>) => {
    const updated = { ...settings, ...partial };
    onUpdateSettings(updated);
    savePersistedVoiceSettings(updated);
  };

  const handleModeChange = (mode: VoiceModeType) => {
    if (mode === 'offline_female') {
      const femaleVoice =
        installedSapiVoices.find((v) => v.is_female)?.name || 'Microsoft Zira Desktop';
      handleUpdate({
        voiceMode: 'offline_female',
        voiceIdentity: 'nova-offline-female',
        selectedVoiceName: `NOVA — Offline Female (${femaleVoice})`,
        offlineVoice: femaleVoice,
        pitch: 1.08,
        speakingRate: 1.05,
      });
    } else {
      const neuralVoice =
        settings.language === 'ta'
          ? 'ta-IN-PallaviNeural'
          : settings.language === 'hi'
          ? 'hi-IN-SwaraNeural'
          : 'en-IN-NeerjaNeural';
      handleUpdate({
        voiceMode: 'neural_female',
        voiceIdentity: 'nova-neural-female',
        selectedVoiceName: `NOVA — Neural Female (${neuralVoice})`,
        neuralVoice: neuralVoice,
        pitch: 1.0,
        speakingRate: 1.05,
      });
    }
  };

  // Preview Voice Action
  const handlePreviewVoice = async () => {
    if (isPreviewPlaying) {
      previewPlayerRef.current?.stop();
      setIsPreviewPlaying(false);
      setIsPreviewLoading(false);
      return;
    }

    setIsPreviewLoading(true);
    setPreviewError(null);

    const isOffline = settings.voiceMode === 'offline_female';
    const lang = settings.language === 'auto' ? 'en-IN' : `${settings.language}-IN`;

    let sampleText = 'Good morning, sir. I am Nova. How may I assist you today?';
    if (settings.language === 'ta') {
      sampleText = 'வணக்கம், நான் நோவா. உங்களுக்கு எவ்வாறு உதவ முடியும்?';
    } else if (settings.language === 'hi') {
      sampleText = 'नमस्ते, मैं நோவா हूँ। मैं आपकी क्या मदद कर सकती हूँ?';
    }

    const voiceTarget = isOffline
      ? settings.offlineVoice || 'Microsoft Zira Desktop'
      : settings.language === 'ta'
      ? 'ta-IN-PallaviNeural'
      : settings.language === 'hi'
      ? 'hi-IN-SwaraNeural'
      : settings.neuralVoice || 'en-IN-NeerjaNeural';

    try {
      if (!previewPlayerRef.current) {
        previewPlayerRef.current = new BackendTTSAudioPlayer();
      }

      await previewPlayerRef.current.previewVoice(
        sampleText,
        {
          language: lang,
          voice: voiceTarget,
          mode: isOffline ? 'offline' : 'neural',
          pitch: settings.pitch,
          speakingRate: settings.speakingRate,
          volume: settings.volume,
          offlineOnly: isOffline,
        },
        (meta) => {
          setIsPreviewLoading(false);
          setIsPreviewPlaying(true);
          setPreviewMeta(meta);
        },
        () => {
          setIsPreviewPlaying(false);
          setIsPreviewLoading(false);
        },
        (err) => {
          setIsPreviewPlaying(false);
          setIsPreviewLoading(false);
          setPreviewError(err.message || 'Speech generation failed.');
        }
      );
    } catch (err: any) {
      setIsPreviewLoading(false);
      setIsPreviewPlaying(false);
      setPreviewError(err.message || 'Speech generation failed.');
    }
  };

  const languages: { code: SupportedLanguageType; label: string; sub: string }[] = [
    { code: 'auto', label: 'Auto-Detect', sub: 'Dynamic code-switching (English, Tamil, Hindi)' },
    { code: 'en', label: 'Indian English', sub: 'Natural en-IN accentuation & cadence' },
    { code: 'ta', label: 'Tamil (தமிழ்)', sub: 'Native Tamil phonetics & Tanglish fluency' },
    { code: 'hi', label: 'Hindi (हिन्दी)', sub: 'Native Hindi phonetics & Hinglish fluency' },
  ];

  const isCurrentModeOffline = settings.voiceMode === 'offline_female';

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/85 backdrop-blur-xl z-50 flex items-center justify-center p-3 sm:p-4 select-none"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0, y: 10 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.95, opacity: 0, y: 10 }}
          onClick={(e) => e.stopPropagation()}
          className={cn(
            'w-full max-w-xl bg-[#030712] border border-cyan-500/40 rounded-3xl p-5 sm:p-6 space-y-5 text-xs font-mono shadow-[0_0_50px_rgba(0,240,255,0.2)] text-slate-100 max-h-[90vh] flex flex-col',
            className
          )}
        >
          {/* Header */}
          <div className="flex items-center justify-between border-b border-cyan-500/20 pb-4 shrink-0">
            <div className="flex items-center space-x-2.5 text-cyan-300 font-extrabold text-sm">
              <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                <Settings className="w-4 h-4" />
              </div>
              <span className="uppercase tracking-wider">Nova Voice Settings</span>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-xl bg-slate-900/80 border border-slate-700/60 text-slate-400 hover:text-white hover:bg-slate-800 transition-all cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Active Voice Status Pill & Mode Indicator */}
          <div className="p-3.5 rounded-2xl bg-cyan-950/40 border border-cyan-500/30 space-y-2 shrink-0">
            <div className="flex items-center justify-between text-[11px]">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse shrink-0" />
                <div className="truncate">
                  <span className="text-slate-400">Active Voice: </span>
                  <span className="text-cyan-300 font-bold uppercase truncate">
                    {isCurrentModeOffline
                      ? `Offline Female (${settings.offlineVoice || 'Microsoft Zira Desktop'})`
                      : `Neural Female (${settings.neuralVoice || 'en-IN-NeerjaNeural'})`}
                  </span>
                </div>
              </div>

              {/* Status Badge */}
              {isCurrentModeOffline ? (
                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-500/40 font-mono font-bold shrink-0">
                  OFFLINE — WINDOWS SAPI
                </span>
              ) : (
                <span className="text-[10px] px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/40 font-mono font-bold shrink-0">
                  ONLINE — EDGE TTS
                </span>
              )}
            </div>

            <div className="flex items-center justify-between text-[10px] text-slate-400 border-t border-cyan-500/10 pt-1.5">
              <span>Language: <strong className="text-slate-200 uppercase">{settings.language}</strong></span>
              <span>Speed: <strong className="text-slate-200">{settings.speakingRate}x</strong></span>
              <span>Pitch: <strong className="text-slate-200">{settings.pitch}</strong></span>
              <span>Volume: <strong className="text-slate-200">{settings.volume}%</strong></span>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center space-x-1.5 p-1 rounded-2xl bg-slate-900/80 border border-slate-800 shrink-0">
            {[
              { id: 'profile' as const, label: 'Voice Mode', icon: UserCheck },
              { id: 'language' as const, label: 'Language', icon: Globe },
              { id: 'speech' as const, label: 'Voice Controls', icon: Volume2 },
              { id: 'interaction' as const, label: 'Hands-Free', icon: Radio },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={cn(
                    'flex-1 py-1.5 rounded-xl flex items-center justify-center space-x-1.5 text-[11px] font-bold transition-all cursor-pointer',
                    isActive
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 shadow-[0_0_10px_rgba(0,240,255,0.2)]'
                      : 'text-slate-400 hover:text-slate-200'
                  )}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">{tab.label}</span>
                </button>
              );
            })}
          </div>

          {/* Tab Content Container */}
          <div className="flex-1 overflow-y-auto space-y-4 pr-1">
            {/* TAB 1: VOICE MODE & SELECTION */}
            {activeTab === 'profile' && (
              <div className="space-y-4">
                <div className="text-[11px] text-slate-400">
                  Select voice mode for Nova's young professional female persona:
                </div>

                {/* Voice Mode Option A: Offline Female Voice (Default) */}
                <div
                  onClick={() => handleModeChange('offline_female')}
                  className={cn(
                    'p-3.5 rounded-2xl border transition-all cursor-pointer space-y-2.5',
                    isCurrentModeOffline
                      ? 'bg-emerald-950/20 border-emerald-500/80 shadow-[0_0_15px_rgba(16,185,129,0.15)]'
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                  )}
                >
                  <div className="flex items-start justify-between space-x-3">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <WifiOff className="w-3.5 h-3.5 text-emerald-400" />
                        <span className="font-bold text-slate-100">Offline Female Voice</span>
                        <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-500/40 font-mono">
                          DEFAULT • 100% LOCAL
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-400 font-sans leading-relaxed">
                        Uses installed Windows SAPI voices with youthful female pitch and speed calibration. Operates completely offline with zero internet.
                      </p>
                    </div>
                    <div
                      className={cn(
                        'w-5 h-5 rounded-full border flex items-center justify-center shrink-0 mt-0.5',
                        isCurrentModeOffline
                          ? 'bg-emerald-500 border-emerald-400 text-black'
                          : 'border-slate-700 bg-slate-950'
                      )}
                    >
                      {isCurrentModeOffline && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                    </div>
                  </div>

                  {/* Installed Windows Voices Dropdown / Selector (Active when offline mode selected) */}
                  {isCurrentModeOffline && (
                    <div
                      className="pt-2 border-t border-emerald-500/20 space-y-1.5"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <div className="text-[10px] text-emerald-300/90 font-bold flex items-center justify-between">
                        <span>Installed Windows SAPI Voices Detected:</span>
                        <span className="text-[9px] text-slate-400">({installedSapiVoices.length} found)</span>
                      </div>
                      <div className="grid grid-cols-1 gap-1.5">
                        {installedSapiVoices.map((voice) => {
                          const isSelectedVoice = (settings.offlineVoice || 'Microsoft Zira Desktop') === voice.name;
                          return (
                            <div
                              key={voice.name}
                              onClick={() =>
                                handleUpdate({
                                  offlineVoice: voice.name,
                                  selectedVoiceName: `NOVA — Offline (${voice.name})`,
                                })
                              }
                              className={cn(
                                'p-2 rounded-xl border text-[11px] flex items-center justify-between transition-all cursor-pointer',
                                isSelectedVoice
                                  ? 'bg-emerald-900/40 border-emerald-400 text-emerald-200'
                                  : 'bg-black/50 border-slate-800 text-slate-300 hover:border-slate-700'
                              )}
                            >
                              <div className="flex items-center space-x-2">
                                <span className="font-bold">{voice.name}</span>
                                <span className="text-[9px] px-1 py-0.2 rounded bg-slate-800 text-slate-300 border border-slate-700">
                                  {voice.culture}
                                </span>
                                {voice.is_female ? (
                                  <span className="text-[9px] px-1 py-0.2 rounded bg-emerald-950 text-emerald-300 border border-emerald-600 font-bold">
                                    FEMALE (RECOMMENDED)
                                  </span>
                                ) : (
                                  <span className="text-[9px] px-1 py-0.2 rounded bg-slate-800 text-slate-400 border border-slate-700">
                                    MALE
                                  </span>
                                )}
                              </div>
                              {isSelectedVoice && <Check className="w-3.5 h-3.5 text-emerald-400" />}
                            </div>
                          );
                        })}
                      </div>
                      <div className="text-[9px] text-slate-500 italic">
                        Note: Windows SAPI voices vary by operating system installation. Microsoft Zira Desktop provides the natural youthful female voice.
                      </div>
                    </div>
                  )}
                </div>

                {/* Voice Mode Option B: Neural Female Voice (Edge TTS Online) */}
                <div
                  onClick={() => handleModeChange('neural_female')}
                  className={cn(
                    'p-3.5 rounded-2xl border transition-all cursor-pointer space-y-2.5',
                    !isCurrentModeOffline
                      ? 'bg-cyan-950/20 border-cyan-400/80 shadow-[0_0_15px_rgba(0,240,255,0.15)]'
                      : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                  )}
                >
                  <div className="flex items-start justify-between space-x-3">
                    <div className="space-y-1">
                      <div className="flex items-center space-x-2">
                        <Wifi className="w-3.5 h-3.5 text-cyan-400" />
                        <span className="font-bold text-slate-100">Neural Female Voice (Edge TTS)</span>
                        <span className="text-[9px] px-1.5 py-0.2 rounded bg-cyan-950 text-cyan-300 border border-cyan-500/40 font-mono">
                          ONLINE (OPTIONAL)
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-400 font-sans leading-relaxed">
                        High-definition natural neural female speech via Microsoft Edge Read Aloud public endpoint. Zero-cost, zero billing, zero accounts. Requires internet connection.
                      </p>
                    </div>
                    <div
                      className={cn(
                        'w-5 h-5 rounded-full border flex items-center justify-center shrink-0 mt-0.5',
                        !isCurrentModeOffline
                          ? 'bg-cyan-500 border-cyan-400 text-black'
                          : 'border-slate-700 bg-slate-950'
                      )}
                    >
                      {!isCurrentModeOffline && <Check className="w-3.5 h-3.5 stroke-[3]" />}
                    </div>
                  </div>

                  {!isCurrentModeOffline && (
                    <div className="pt-2 border-t border-cyan-500/20 space-y-1.5 text-[10px]">
                      <div className="text-cyan-300 font-bold">Supported Multilingual Female Neural Voices:</div>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-1.5">
                        <div className="p-2 rounded-xl bg-black/50 border border-cyan-500/30 text-slate-200">
                          <div className="text-cyan-400 font-bold">English (India)</div>
                          <div className="text-[10px] text-slate-300 font-mono">en-IN-NeerjaNeural</div>
                          <div className="text-[9px] text-slate-500">Youthful Professional</div>
                        </div>
                        <div className="p-2 rounded-xl bg-black/50 border border-cyan-500/30 text-slate-200">
                          <div className="text-cyan-400 font-bold">Tamil (India)</div>
                          <div className="text-[10px] text-slate-300 font-mono">ta-IN-PallaviNeural</div>
                          <div className="text-[9px] text-slate-500">Natural Tanglish</div>
                        </div>
                        <div className="p-2 rounded-xl bg-black/50 border border-cyan-500/30 text-slate-200">
                          <div className="text-cyan-400 font-bold">Hindi (India)</div>
                          <div className="text-[10px] text-slate-300 font-mono">hi-IN-SwaraNeural</div>
                          <div className="text-[9px] text-slate-500">Natural Hinglish</div>
                        </div>
                      </div>
                      <div className="text-[9px] text-slate-500 italic">
                        Disclosure: Edge TTS connects to Microsoft's public read-aloud servers and is not local.
                      </div>
                    </div>
                  )}
                </div>

                {/* PREVIEW VOICE ACTION SECTION */}
                <div className="p-3.5 rounded-2xl bg-black/60 border border-cyan-500/30 space-y-2">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-bold text-slate-200 flex items-center space-x-1.5">
                        <Volume2 className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Voice Preview</span>
                      </div>
                      <div className="text-[10px] text-slate-400 font-sans">
                        Generate and play live speech through the selected provider:
                      </div>
                    </div>

                    <button
                      onClick={handlePreviewVoice}
                      disabled={isPreviewLoading}
                      className={cn(
                        'px-3.5 py-1.5 rounded-xl font-bold flex items-center space-x-1.5 transition-all cursor-pointer',
                        isPreviewPlaying
                          ? 'bg-rose-500/20 border border-rose-500 text-rose-300'
                          : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-[0_0_15px_rgba(0,240,255,0.3)]'
                      )}
                    >
                      {isPreviewLoading ? (
                        <>
                          <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          <span>Synthesizing...</span>
                        </>
                      ) : isPreviewPlaying ? (
                        <>
                          <Square className="w-3.5 h-3.5 fill-current" />
                          <span>Stop</span>
                        </>
                      ) : (
                        <>
                          <Play className="w-3.5 h-3.5 fill-current" />
                          <span>Preview Voice</span>
                        </>
                      )}
                    </button>
                  </div>

                  {/* Provider Status Result during/after Preview */}
                  {previewMeta && !previewError && (
                    <div className="p-2 rounded-xl bg-slate-900/80 border border-slate-700 flex items-center justify-between text-[10px]">
                      <div className="flex items-center space-x-2">
                        <span className="text-slate-400">Provider Status:</span>
                        <span
                          className={cn(
                            'font-bold px-1.5 py-0.2 rounded',
                            previewMeta.mode === 'offline'
                              ? 'bg-emerald-950 text-emerald-300 border border-emerald-500/40'
                              : 'bg-cyan-950 text-cyan-300 border border-cyan-500/40'
                          )}
                        >
                          {previewMeta.mode === 'offline' ? 'OFFLINE (Windows SAPI)' : 'ONLINE (Edge TTS)'}
                        </span>
                      </div>
                      <span className="text-slate-300 font-mono truncate max-w-[200px]">
                        Voice: {previewMeta.voice}
                      </span>
                    </div>
                  )}

                  {/* Preview Error Notice */}
                  {previewError && (
                    <div className="p-2.5 rounded-xl bg-rose-950/40 border border-rose-500/50 text-rose-300 text-[10px] flex items-start space-x-2">
                      <AlertCircle className="w-3.5 h-3.5 text-rose-400 shrink-0 mt-0.5" />
                      <div>
                        <strong>ERROR — speech generation failed:</strong> {previewError}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* TAB 2: LANGUAGE */}
            {activeTab === 'language' && (
              <div className="space-y-3">
                <div className="text-[11px] text-slate-400">
                  Select preferred language foundation or enable dynamic code-switching:
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {languages.map((lang) => {
                    const isSelected = settings.language === lang.code;
                    return (
                      <div
                        key={lang.code}
                        onClick={() => handleUpdate({ language: lang.code })}
                        className={cn(
                          'p-3 rounded-2xl border transition-all cursor-pointer flex items-center justify-between',
                          isSelected
                            ? 'bg-cyan-950/40 border-cyan-400/80 shadow-[0_0_15px_rgba(0,240,255,0.2)]'
                            : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                        )}
                      >
                        <div>
                          <div className="font-bold text-slate-100">{lang.label}</div>
                          <div className="text-[10px] text-slate-400 font-sans">{lang.sub}</div>
                        </div>
                        <div
                          className={cn(
                            'w-4.5 h-4.5 rounded-full border flex items-center justify-center shrink-0 ml-2',
                            isSelected
                              ? 'bg-cyan-500 border-cyan-400 text-black'
                              : 'border-slate-700 bg-slate-950'
                          )}
                        >
                          {isSelected && <Check className="w-3 h-3 stroke-[3]" />}
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className="p-3 rounded-2xl bg-slate-900/40 border border-slate-800 text-[10px] text-slate-400 space-y-1">
                  <span className="text-cyan-300 font-bold">Multilingual Young Female Delivery: </span>
                  When switching languages, Nova speaks using the authentic native female voice matching the language:
                  English uses Neerja (or Zira offline), Tamil uses Pallavi, and Hindi uses Swara.
                </div>
              </div>
            )}

            {/* TAB 3: VOICE CONTROLS (Speed, Pitch, Volume) */}
            {activeTab === 'speech' && (
              <div className="space-y-4">
                {/* Speaking Rate */}
                <div className="space-y-1.5">
                  <div className="flex justify-between items-center text-slate-300">
                    <span>Speech Speed (Cadence):</span>
                    <span className="text-cyan-400 font-bold">{settings.speakingRate}x</span>
                  </div>
                  <input
                    type="range"
                    min="0.8"
                    max="1.3"
                    step="0.05"
                    value={settings.speakingRate}
                    onChange={(e) => handleUpdate({ speakingRate: parseFloat(e.target.value) })}
                    className="w-full accent-cyan-400 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-slate-500">
                    <span>Measured (0.8x)</span>
                    <span>Youthful Natural (1.05x)</span>
                    <span>Brisk (1.3x)</span>
                  </div>
                </div>

                {/* Pitch (Calibrated for young female tone) */}
                <div className="space-y-1.5">
                  <div className="flex justify-between items-center text-slate-300">
                    <span>Vocal Pitch (Youthful Elevation):</span>
                    <span className="text-cyan-400 font-bold">{settings.pitch}</span>
                  </div>
                  <input
                    type="range"
                    min="0.85"
                    max="1.25"
                    step="0.02"
                    value={settings.pitch}
                    onChange={(e) => handleUpdate({ pitch: parseFloat(e.target.value) })}
                    className="w-full accent-cyan-400 cursor-pointer"
                  />
                  <div className="flex justify-between text-[10px] text-slate-500">
                    <span>Deeper (0.85)</span>
                    <span>Youthful Female (1.08)</span>
                    <span>High (1.25)</span>
                  </div>
                  <div className="text-[9px] text-slate-500">
                    Tuning note: Elevated pitch (+8%) produces a vibrant, youthful, natural tone on Windows SAPI & Edge TTS.
                  </div>
                </div>

                {/* Volume */}
                <div className="space-y-1.5">
                  <div className="flex justify-between items-center text-slate-300">
                    <span>Speech Synthesis Volume:</span>
                    <span className="text-cyan-400 font-bold">{settings.volume}%</span>
                  </div>
                  <input
                    type="range"
                    min="10"
                    max="100"
                    step="5"
                    value={settings.volume}
                    onChange={(e) => handleUpdate({ volume: parseInt(e.target.value, 10) })}
                    className="w-full accent-cyan-400 cursor-pointer"
                  />
                </div>

                {/* Response Length Preference */}
                <div className="space-y-1.5">
                  <div className="text-slate-300 font-bold">Verbal Conciseness:</div>
                  <div className="grid grid-cols-2 gap-2">
                    {[
                      { id: 'concise' as const, label: 'Concise (Default)', sub: 'Direct, brief conversational answers' },
                      { id: 'detailed' as const, label: 'Detailed', sub: 'Comprehensive explanations' },
                    ].map((opt) => (
                      <div
                        key={opt.id}
                        onClick={() => handleUpdate({ responseLength: opt.id })}
                        className={cn(
                          'p-2.5 rounded-xl border transition-all cursor-pointer',
                          settings.responseLength === opt.id
                            ? 'bg-cyan-950/40 border-cyan-400 text-cyan-300'
                            : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:text-slate-200'
                        )}
                      >
                        <div className="font-bold">{opt.label}</div>
                        <div className="text-[10px] font-sans opacity-80">{opt.sub}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* TAB 4: HANDS-FREE & INTERACTION */}
            {activeTab === 'interaction' && (
              <div className="space-y-3">
                {/* Wake Phrase Config */}
                <div className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-slate-200">Acoustic Wake Phrase</span>
                    <span className="text-[10px] text-cyan-400 font-mono">Current: "{settings.wakePhrase}"</span>
                  </div>
                  <input
                    type="text"
                    value={settings.wakePhrase}
                    onChange={(e) => handleUpdate({ wakePhrase: e.target.value })}
                    placeholder="e.g. Hey Nova"
                    className="w-full px-3 py-1.5 rounded-xl bg-black border border-cyan-500/40 text-slate-100 text-xs focus:outline-none focus:border-cyan-400 font-mono"
                  />
                  <div className="text-[10px] text-slate-500">
                    Activates Nova when spoken naturally (also matches short keyword "Nova").
                  </div>
                </div>

                {/* Barge-In Interruption */}
                <div
                  onClick={() => handleUpdate({ allowInterrupt: !settings.allowInterrupt })}
                  className="flex items-center justify-between p-3 rounded-2xl bg-slate-900/80 border border-slate-800 cursor-pointer"
                >
                  <div>
                    <div className="font-bold text-slate-200">Voice Interruption (Barge-In)</div>
                    <div className="text-[10px] text-slate-500 font-sans">
                      Say "Stop", "Nova wait", or "Be quiet" while Nova is speaking to halt immediately
                    </div>
                  </div>
                  <div
                    className={cn(
                      'w-10 h-6 rounded-full border p-0.5 transition-colors flex items-center',
                      settings.allowInterrupt
                        ? 'bg-cyan-500/20 border-cyan-500 justify-end'
                        : 'bg-slate-950 border-slate-800 justify-start'
                    )}
                  >
                    <div
                      className={cn(
                        'w-4.5 h-4.5 rounded-full',
                        settings.allowInterrupt ? 'bg-cyan-400' : 'bg-slate-600'
                      )}
                    />
                  </div>
                </div>

                {/* VAD Sensitivity */}
                <div className="p-3 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
                  <div className="font-bold text-slate-200">Voice Activity Detection (VAD) Sensitivity</div>
                  <div className="grid grid-cols-3 gap-2">
                    {(['low', 'medium', 'high'] as const).map((lvl) => (
                      <button
                        key={lvl}
                        onClick={() => handleUpdate({ vadSensitivity: lvl })}
                        className={cn(
                          'py-1.5 rounded-xl border text-[11px] font-bold uppercase cursor-pointer transition-all',
                          settings.vadSensitivity === lvl
                            ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400'
                            : 'bg-slate-950 border-slate-800 text-slate-400'
                        )}
                      >
                        {lvl}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Footer Save & Dismiss */}
          <div className="pt-3 border-t border-slate-800 flex justify-end shrink-0">
            <button
              onClick={onClose}
              className="px-5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold transition-all shadow-[0_0_15px_rgba(0,240,255,0.4)] cursor-pointer"
            >
              Done
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default VoiceSettings;
