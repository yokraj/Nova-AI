import React, { useState } from 'react';
import { useVoiceInteraction } from '../hooks/useVoiceInteraction';
import { useVoiceKeyboard } from '../hooks/useVoiceKeyboard';
import VoiceOrb from './VoiceOrb';
import VoiceStatus from './VoiceStatus';
import VoiceWaveform from './VoiceWaveform';
import VoiceTranscript from './VoiceTranscript';
import VoiceResponse from './VoiceResponse';
import VoiceControls from './VoiceControls';
import VoiceSettings from './VoiceSettings';
import VoicePermissionDialog from './VoicePermissionDialog';

interface VoiceInterfaceProps {
  onSendToConversation?: (prompt: string) => void;
  onSwitchToText?: () => void;
  className?: string;
}

export const VoiceInterface: React.FC<VoiceInterfaceProps> = ({
  onSendToConversation,
  onSwitchToText,
  className,
}) => {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const voice = useVoiceInteraction(onSendToConversation);

  // Register Push-To-Talk keyboard listener
  useVoiceKeyboard(
    voice.settings.pushToTalk,
    () => voice.startListeningSession(),
    () => voice.stopListeningSession()
  );

  return (
    <div className="min-h-[85vh] flex flex-col items-center justify-between py-6 px-4 relative overflow-hidden select-none">
      {/* Background Cyber Ambient Glow */}
      <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Top Voice Header & State */}
      <div className="w-full max-w-xl flex items-center justify-between z-10 font-mono text-xs">
        <div className="flex items-center space-x-2">
          <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-ping" />
          <span className="text-cyan-300 font-bold tracking-wider">VOICE ENGINE READY</span>
        </div>
        <button
          onClick={() => setIsSettingsOpen(true)}
          className="text-slate-400 hover:text-cyan-300 text-[11px] underline cursor-pointer"
        >
          Voice Config ({voice.settings.language})
        </button>
      </div>

      {/* Main Center Nova Core Orb Visual Identity & Waveform */}
      <div className="flex flex-col items-center justify-center space-y-4 my-4 z-10 max-w-xl text-center">
        <VoiceOrb
          state={voice.voiceState}
          onClick={voice.startListeningSession}
        />

        <VoiceStatus state={voice.voiceState} />

        <VoiceWaveform state={voice.voiceState} />
      </div>

      {/* Live Speech Transcript (During Listening) */}
      <VoiceTranscript
        transcript={voice.liveTranscript}
        isListening={voice.voiceState === 'LISTENING'}
      />

      {/* Spoken Voice Response Card (During Speaking/Paused) */}
      {(voice.voiceState === 'SPEAKING' || voice.voiceState === 'PAUSED' || voice.lastSpokenText) && (
        <div className="w-full z-10 my-2">
          <VoiceResponse
            text={voice.lastSpokenText}
            state={voice.voiceState}
            progress={voice.playbackProgress}
            onPause={voice.pausePlayback}
            onResume={voice.resumePlayback}
            onInterrupt={voice.interruptSpeech}
          />
        </div>
      )}

      {/* Primary Voice Controls */}
      <div className="w-full max-w-xl z-10 my-4">
        <VoiceControls
          state={voice.voiceState}
          onToggleMic={() => {
            if (voice.voiceState === 'LISTENING') {
              voice.stopListeningSession();
            } else {
              voice.startListeningSession();
            }
          }}
          onOpenSettings={() => setIsSettingsOpen(true)}
          onSwitchToText={onSwitchToText}
          continuousMode={voice.settings.continuousConversation}
          onToggleContinuous={() =>
            voice.setSettings({
              ...voice.settings,
              continuousConversation: !voice.settings.continuousConversation,
            })
          }
        />
      </div>

      {/* Voice Settings Modal */}
      <VoiceSettings
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        settings={voice.settings}
        onUpdateSettings={voice.setSettings}
      />

      {/* Microphone Permission Modal */}
      <VoicePermissionDialog
        permissionState={voice.permissionState}
        onGrantPermission={() => voice.setPermissionState('granted')}
        onDenyPermission={() => voice.setPermissionState('denied')}
      />
    </div>
  );
};

export default VoiceInterface;
