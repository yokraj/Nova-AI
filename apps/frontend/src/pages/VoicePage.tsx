import React from 'react';
import { useNavigate } from 'react-router-dom';
import VoiceInterface from '@/features/voice/components/VoiceInterface';

export const VoicePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <VoiceInterface
      onSwitchToText={() => navigate('/chat')}
    />
  );
};

export default VoicePage;
