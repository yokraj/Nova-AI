/**
 * Real Microphone Audio Capture Service.
 * Manages getUserMedia stream lifecycle, MediaRecorder audio chunking,
 * and tracks release to prevent persistent microphone locks.
 */

export class MicrophoneError extends Error {
  constructor(message: string, public code: 'PERMISSION_DENIED' | 'NOT_FOUND' | 'UNSUPPORTED' | 'RECORDING_ERROR') {
    super(message);
    this.name = 'MicrophoneError';
  }
}

export class AudioCaptureService {
  private mediaStream: MediaStream | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private recordedChunks: Blob[] = [];
  private isRecordingActive = false;

  isSupported(): boolean {
    return (
      typeof window !== 'undefined' &&
      typeof navigator !== 'undefined' &&
      Boolean(navigator.mediaDevices?.getUserMedia) &&
      typeof MediaRecorder !== 'undefined'
    );
  }

  async start(): Promise<void> {
    if (!this.isSupported()) {
      throw new MicrophoneError(
        'Audio recording is not supported in this browser environment.',
        'UNSUPPORTED'
      );
    }

    // Stop any existing stream
    this.cancel();

    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
    } catch (err: any) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        throw new MicrophoneError(
          'Microphone permission denied. Please allow microphone access in your browser settings.',
          'PERMISSION_DENIED'
        );
      }
      if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        throw new MicrophoneError(
          'No microphone hardware detected on this device.',
          'NOT_FOUND'
        );
      }
      throw new MicrophoneError(
        err.message || 'Failed to acquire microphone audio stream.',
        'RECORDING_ERROR'
      );
    }

    // Determine optimal supported audio mimeType
    let mimeType = 'audio/webm';
    if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
      mimeType = 'audio/webm;codecs=opus';
    } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
      mimeType = 'audio/ogg;codecs=opus';
    } else if (MediaRecorder.isTypeSupported('audio/wav')) {
      mimeType = 'audio/wav';
    }

    this.recordedChunks = [];
    try {
      this.mediaRecorder = new MediaRecorder(this.mediaStream, { mimeType });
      this.mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data && event.data.size > 0) {
          this.recordedChunks.push(event.data);
        }
      };

      this.mediaRecorder.start(100); // 100ms time slice for streaming chunks
      this.isRecordingActive = true;
    } catch (err: any) {
      this.cancel();
      throw new MicrophoneError(
        `Failed to start MediaRecorder: ${err.message}`,
        'RECORDING_ERROR'
      );
    }
  }

  async stop(): Promise<Blob | null> {
    if (!this.mediaRecorder || !this.isRecordingActive) {
      this.cancel();
      return null;
    }

    return new Promise<Blob | null>((resolve) => {
      if (!this.mediaRecorder) {
        resolve(null);
        return;
      }

      this.mediaRecorder.onstop = () => {
        const mimeType = this.mediaRecorder?.mimeType || 'audio/webm';
        const audioBlob = new Blob(this.recordedChunks, { type: mimeType });
        this.releaseResources();
        if (audioBlob.size < 100) {
          resolve(null);
        } else {
          resolve(audioBlob);
        }
      };

      try {
        if (this.mediaRecorder.state !== 'inactive') {
          this.mediaRecorder.stop();
        } else {
          this.releaseResources();
          resolve(null);
        }
      } catch {
        this.releaseResources();
        resolve(null);
      }
    });
  }

  cancel(): void {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      try {
        this.mediaRecorder.stop();
      } catch {
        // ignore
      }
    }
    this.releaseResources();
  }

  isRecording(): boolean {
    return this.isRecordingActive;
  }

  private releaseResources(): void {
    this.isRecordingActive = false;
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }
    this.mediaRecorder = null;
    this.recordedChunks = [];
  }
}

