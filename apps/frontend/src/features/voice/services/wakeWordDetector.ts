/**
 * Dedicated Wake Word Detection Service for Nova-AI Hands-Free Assistant.
 * Provides continuous local-first keyword detection ("Hey Nova", "Nova", or custom wake phrase),
 * command prefix stripping, and re-trigger protection.
 */

import { APP_CONFIG } from '@/config/app.config';

export interface WakeWordMatchResult {
  detected: boolean;
  keyword: string;
  confidence: number;
  strippedCommand: string;
  rawText: string;
}

export interface WakeWordDetectorOptions {
  wakePhrase?: string;
  onWakeWordDetected?: (result: WakeWordMatchResult) => void;
  apiBaseUrl?: string;
}

export class WakeWordDetector {
  private wakePhrase: string;
  private onWakeWordDetected?: (result: WakeWordMatchResult) => void;
  private apiBaseUrl: string;
  private isProcessing = false;
  private lastTriggerTimestamp = 0;
  private triggerCooldownMs = 2500; // Prevent rapid duplicate wake triggers

  constructor(options: WakeWordDetectorOptions = {}) {
    this.wakePhrase = (options.wakePhrase || 'Hey Nova').trim();
    this.onWakeWordDetected = options.onWakeWordDetected;
    this.apiBaseUrl = options.apiBaseUrl || APP_CONFIG.apiBaseUrl;
  }

  setWakePhrase(phrase: string): void {
    if (phrase && phrase.trim()) {
      this.wakePhrase = phrase.trim();
    }
  }

  getWakePhrase(): string {
    return this.wakePhrase;
  }

  /**
   * Fast client-side lexical/phonetic pattern matching to detect wake phrase in text.
   * Strips wake phrase prefix cleanly and returns any trailing command.
   */
  matchInText(rawText: string): WakeWordMatchResult {
    const text = rawText.trim();
    if (!text) {
      return { detected: false, keyword: '', confidence: 0, strippedCommand: '', rawText };
    }

    const lower = text.toLowerCase();
    const targetPhrase = this.wakePhrase.toLowerCase();

    // Build candidate keywords: primary wake phrase + singular keyword if phrase is "hey <word>"
    const keywords = [targetPhrase];
    if (targetPhrase.startsWith('hey ')) {
      keywords.push(targetPhrase.replace('hey ', '').trim());
    } else if (targetPhrase === 'nova') {
      keywords.unshift('hey nova');
    }

    // Sort longest first to match "hey nova" before "nova"
    keywords.sort((a, b) => b.length - a.length);

    for (const kw of keywords) {
      // 1. Prefix match (e.g. "Hey Nova, what time is it?" or "Hey Nova")
      const prefixRegex = new RegExp(`^(?:hey\\s+)?${this.escapeRegex(kw)}[\\s,:\\.!-]*`, 'i');
      const match = lower.match(prefixRegex);
      if (match) {
        const stripped = text.slice(match[0].length).trim();
        return {
          detected: true,
          keyword: kw,
          confidence: 0.98,
          strippedCommand: stripped,
          rawText: text,
        };
      }

      // 2. Contains wake phrase within first 4 words (e.g. "Okay hey nova open files")
      const words = lower.split(/\s+/);
      const kwWords = kw.split(/\s+/);
      const searchWindow = words.slice(0, 5).join(' ');
      if (searchWindow.includes(kw)) {
        // Strip out the keyword from text
        const removeRegex = new RegExp(`\\b(?:hey\\s+)?${this.escapeRegex(kw)}\\b[\\s,:\\.!-]*`, 'i');
        const stripped = text.replace(removeRegex, '').trim();
        return {
          detected: true,
          keyword: kw,
          confidence: 0.92,
          strippedCommand: stripped,
          rawText: text,
        };
      }
    }

    return { detected: false, keyword: '', confidence: 0, strippedCommand: '', rawText: text };
  }

  /**
   * Checks audio payload against the local backend wake-word endpoint.
   * 100% offline, local faster-whisper fast keyword evaluation.
   */
  async evaluateAudioBlob(blob: Blob): Promise<WakeWordMatchResult> {
    if (this.isProcessing) {
      return { detected: false, keyword: '', confidence: 0, strippedCommand: '', rawText: '' };
    }

    const now = performance.now();
    if (now - this.lastTriggerTimestamp < this.triggerCooldownMs) {
      return { detected: false, keyword: '', confidence: 0, strippedCommand: '', rawText: '' };
    }

    this.isProcessing = true;

    try {
      const formData = new FormData();
      formData.append('file', blob, 'wake_check.webm');

      const url = `${this.apiBaseUrl}/voice/wake-word/detect?wake_phrase=${encodeURIComponent(
        this.wakePhrase
      )}`;
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Wake word backend returned HTTP ${response.status}`);
      }

      const data = await response.json();
      const result: WakeWordMatchResult = {
        detected: Boolean(data.detected),
        keyword: data.keyword || this.wakePhrase,
        confidence: Number(data.confidence || 0),
        strippedCommand: data.stripped_command || '',
        rawText: data.raw_transcript || '',
      };

      if (result.detected) {
        this.lastTriggerTimestamp = performance.now();
        if (this.onWakeWordDetected) {
          this.onWakeWordDetected(result);
        }
      }

      return result;
    } catch (err) {
      console.warn('Backend audio wake-word check failed, falling back to local client parsing:', err);
      return { detected: false, keyword: '', confidence: 0, strippedCommand: '', rawText: '' };
    } finally {
      this.isProcessing = false;
    }
  }

  /**
   * Evaluates incoming text transcript (from interim stream or local Whisper)
   * and dispatches wake callback if triggered.
   */
  evaluateText(transcript: string): WakeWordMatchResult {
    const now = performance.now();
    if (now - this.lastTriggerTimestamp < this.triggerCooldownMs) {
      return { detected: false, keyword: '', confidence: 0, strippedCommand: '', rawText: transcript };
    }

    const result = this.matchInText(transcript);
    if (result.detected) {
      this.lastTriggerTimestamp = performance.now();
      if (this.onWakeWordDetected) {
        this.onWakeWordDetected(result);
      }
    }
    return result;
  }

  private escapeRegex(str: string): string {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
}

