import { useEffect, useRef } from 'react';

export function useVoiceKeyboard(
  isPushToTalkEnabled: boolean,
  onStartTalk: () => void,
  onStopTalk: () => void
) {
  const isKeyDownRef = useRef(false);

  useEffect(() => {
    if (!isPushToTalkEnabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Do not trigger if typing inside input, textarea, or contenteditable
      const target = e.target as HTMLElement;
      if (target && (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable)) {
        return;
      }

      if (e.code === 'Space' && !isKeyDownRef.current) {
        e.preventDefault();
        isKeyDownRef.current = true;
        onStartTalk();
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.code === 'Space' && isKeyDownRef.current) {
        e.preventDefault();
        isKeyDownRef.current = false;
        onStopTalk();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [isPushToTalkEnabled, onStartTalk, onStopTalk]);
}
