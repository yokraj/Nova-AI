/**
 * Real Microphone Audio Capture Service.
 * Manages getUserMedia stream lifecycle, MediaRecorder audio chunking,
 * continuous stream reuse for VAD, mute controls, and hardware track release.
 */

export class MicrophoneError extends Error {
  constructor(
    message: string,
    public code: 'PERMISSION_DENIED' | 'NOT_FOUND' | 'UNSUPPORTED' | 'RECORDING_ERROR'
  ) {
    super(message);
    this.name = 'MicrophoneError';
  }
}

export class AudioCaptureService {
  private mediaStream: MediaStream | null = null;
  private mediaRecorder: MediaRecorder | null = null;
  private recordedChunks: Blob[] = [];
  private isRecordingActive = false;
  private isMutedState = false;

  isSupported(): boolean {
    return (
      typeof window !== 'undefined' &&
      typeof navigator !== 'undefined' &&
      Boolean(navigator.mediaDevices?.getUserMedia) &&
      typeof MediaRecorder !== 'undefined'
    );
  }

  /**
   * Acquires the hardware audio MediaStream once.
   * If a stream is already active and healthy, returns it immediately to prevent duplicate streams.
   */
  async acquireContinuousStream(): Promise<MediaStream> {
    if (!this.isSupported()) {
      throw new MicrophoneError(
        'Audio recording is not supported in this browser environment.',
        'UNSUPPORTED'
      );
    }

    if (this.mediaStream && this.mediaStream.active) {
      const activeTracks = this.mediaStream.getAudioTracks().filter((t) => t.readyState === 'live');
      if (activeTracks.length > 0) {
        return this.mediaStream;
      }
    }

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
      this.isMutedState = false;
      return this.mediaStream;
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
  }

  getStream(): MediaStream | null {
    if (this.mediaStream && this.mediaStream.active) {
      return this.mediaStream;
    }
    return null;
  }

  /**
   * Starts capturing an utterance recording on the continuous stream.
   */
  async startRecordingSlice(): Promise<void> {
    const stream = await this.acquireContinuousStream();

    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      try {
        this.mediaRecorder.stop();
      } catch {}
    }

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
      this.mediaRecorder = new MediaRecorder(stream, { mimeType });
      this.mediaRecorder.ondataavailable = (event: BlobEvent) => {
        if (event.data && event.data.size > 0) {
          this.recordedChunks.push(event.data);
        }
      };

      this.mediaRecorder.start(100);
      this.isRecordingActive = true;
    } catch (err: any) {
      this.isRecordingActive = false;
      throw new MicrophoneError(
        `Failed to start MediaRecorder: ${err.message}`,
        'RECORDING_ERROR'
      );
    }
  }

  /**
   * Stops capturing an utterance and returns the audio Blob without stopping the underlying MediaStream.
   */
  async stopRecordingSlice(): Promise<Blob | null> {
    if (!this.mediaRecorder || !this.isRecordingActive) {
      this.isRecordingActive = false;
      return null;
    }

    return new Promise<Blob | null>((resolve) => {
      const recorder = this.mediaRecorder;
      if (!recorder) {
        this.isRecordingActive = false;
        resolve(null);
        return;
      }

      recorder.onstop = () => {
        this.isRecordingActive = false;
        const mimeType = recorder.mimeType || 'audio/webm';
        const audioBlob = new Blob(this.recordedChunks, { type: mimeType });
        this.recordedChunks = [];
        if (audioBlob.size < 100) {
          resolve(null);
        } else {
          resolve(audioBlob);
        }
      };

      try {
        if (recorder.state !== 'inactive') {
          recorder.stop();
        } else {
          this.isRecordingActive = false;
          resolve(null);
        }
      } catch {
        this.isRecordingActive = false;
        resolve(null);
      }
    });
  }

  /**
   * Standard single-shot start (for push-to-talk mode).
   */
  async start(): Promise<void> {
    await this.startRecordingSlice();
  }

  /**
   * Standard single-shot stop (for push-to-talk mode). Releases stream.
   */
  async stop(): Promise<Blob | null> {
    const blob = await this.stopRecordingSlice();
    this.releaseResources();
    return blob;
  }

  /**
   * Mute microphone input without stopping the stream.
   */
  mute(): void {
    if (this.mediaStream) {
      this.mediaStream.getAudioTracks().forEach((track) => {
        track.enabled = false;
      });
      this.isMutedState = true;
    }
  }

  /**
   * Unmute microphone input.
   */
  unmute(): void {
    if (this.mediaStream) {
      this.mediaStream.getAudioTracks().forEach((track) => {
        track.enabled = true;
      });
      this.isMutedState = false;
    }
  }

  isMuted(): boolean {
    return this.isMutedState;
  }

  /**
   * Completely cancel recording and release hardware microphone indicators.
   */
  cancel(): void {
    if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
      try {
        this.mediaRecorder.stop();
      } catch {}
    }
    this.releaseResources();
  }

  isRecording(): boolean {
    return this.isRecordingActive;
  }

  releaseResources(): void {
    this.isRecordingActive = false;
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => {
        try {
          track.stop();
        } catch {}
      });
      this.mediaStream = null;
    }
    this.mediaRecorder = null;
    this.recordedChunks = [];
  }
}
