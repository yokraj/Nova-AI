/**
 * Natural Speech Preparation and Response Formatter for Nova AI.
 * Transforms raw markdown/technical AI output into natural, conversational,
 * cadence-aware speech scripts with abbreviation expansion, currency normalization,
 * code stripping, and breath-boundary segmentation.
 */

export interface FormattedSpeechOutput {
  displayText: string;       // Original or clean text for UI markdown display
  speechText: string;        // Fully normalized single script for text-to-speech
  speechChunks: string[];    // Natural breath-pause segments for low-latency sequential playback
  detectedLanguage: string;  // Detected or inferred language code ('en', 'ta', 'hi', etc.)
}

export class SpeechPreparationService {
  /**
   * Common technical abbreviations expanded to natural spoken English.
   */
  private static readonly ABBREVIATIONS: Record<string, string> = {
    '\\bAPI\\b': 'A P I',
    '\\bAPIs\\b': 'A P Is',
    '\\bUI\\b': 'U I',
    '\\bUX\\b': 'U X',
    '\\bOS\\b': 'O S',
    '\\bCPU\\b': 'C P U',
    '\\bCPUs\\b': 'C P Us',
    '\\bGPU\\b': 'G P U',
    '\\bGPUs\\b': 'G P Us',
    '\\bRAM\\b': 'RAM',
    '\\bROM\\b': 'ROM',
    '\\bURL\\b': 'U R L',
    '\\bURLs\\b': 'U R Ls',
    '\\bHTTP\\b': 'H T T P',
    '\\bHTTPS\\b': 'H T T P S',
    '\\bHTML\\b': 'H T M L',
    '\\bCSS\\b': 'C S S',
    '\\bCLI\\b': 'C L I',
    '\\bSDK\\b': 'S D K',
    '\\bSDKs\\b': 'S D Ks',
    '\\bJSON\\b': 'JSON',
    '\\bSQL\\b': 'S Q L',
    '\\bREST\\b': 'REST',
    '\\bLLM\\b': 'L L M',
    '\\bLLMs\\b': 'L L Ms',
    '\\bAI\\b': 'A I',
    '\\bML\\b': 'M L',
    '\\bVAD\\b': 'V A D',
    '\\bSTT\\b': 'S T T',
    '\\bTTS\\b': 'T T S',
    '\\be\\.g\\.\\b': 'for example',
    '\\bi\\.e\\.\\b': 'that is',
    '\\betc\\.\\b': 'etcetera',
    '\\bvs\\.\\b': 'versus',
  };

  /**
   * Currency patterns to spoken form.
   */
  private static normalizeCurrency(text: string): string {
    return text
      // Rupees: ₹500, Rs. 500, INR 500
      .replace(/(?:₹|Rs\.?\s*|INR\s*)(\d+(?:,\d+)*(?:\.\d+)?)/gi, '$1 rupees')
      // Dollars: $100
      .replace(/\$(\d+(?:,\d+)*(?:\.\d+)?)/g, '$1 dollars')
      // Euros: €50
      .replace(/€(\d+(?:,\d+)*(?:\.\d+)?)/g, '$1 euros')
      // Pounds: £50
      .replace(/£(\d+(?:,\d+)*(?:\.\d+)?)/g, '$1 pounds')
      // Percentages: 99%
      .replace(/(\d+(?:\.\d+)?)%/g, '$1 percent');
  }

  /**
   * Units of measurement to spoken form.
   */
  private static normalizeUnits(text: string): string {
    return text
      .replace(/\b(\d+)\s*ms\b/gi, '$1 milliseconds')
      .replace(/\b(\d+)\s*sec\b/gi, '$1 seconds')
      .replace(/\b(\d+)\s*km\/h\b/gi, '$1 kilometers per hour')
      .replace(/\b(\d+)\s*km\b/gi, '$1 kilometers')
      .replace(/\b(\d+)\s*gb\b/gi, '$1 gigabytes')
      .replace(/\b(\d+)\s*mb\b/gi, '$1 megabytes')
      .replace(/\b(\d+)\s*kb\b/gi, '$1 kilobytes')
      .replace(/\b(\d+)\s*ghz\b/gi, '$1 gigahertz')
      .replace(/\b(\d+)\s*mhz\b/gi, '$1 megahertz');
  }

  /**
   * Code formatting and technical symbols cleaned for natural speech.
   */
  private static cleanTechnicalArtifacts(text: string): string {
    let cleaned = text;

    // 1. Remove <think>...</think> chain-of-thought blocks completely
    cleaned = cleaned.replace(/<think>[\s\S]*?<\/think>/gi, '');

    // 2. Replace multi-line code blocks with a polite conversational announcement
    cleaned = cleaned.replace(/```[a-z]*\s*([\s\S]*?)```/gi, (_match, codeContent) => {
      const lineCount = codeContent.trim().split('\n').length;
      if (lineCount <= 2) {
        return ' ' + codeContent.replace(/[{}\[\]();=]/g, ' ').trim() + ' ';
      }
      return ' I have displayed the code on screen. ';
    });

    // 3. Inline code blocks `my_var` -> my var
    cleaned = cleaned.replace(/`([^`]+)`/g, (_match, token) => {
      // Split camelCase or snake_case for natural pronunciation
      return token
        .replace(/_/g, ' ')
        .replace(/([a-z])([A-Z])/g, '$1 $2')
        .replace(/[(){}\[\];:]/g, '');
    });

    // 4. Markdown links [Title](url) -> Title
    cleaned = cleaned.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');

    // 5. Bare URLs https://... -> "the link"
    cleaned = cleaned.replace(/https?:\/\/(?:www\.)?([a-zA-Z0-9-]+\.[a-zA-Z]{2,})(?:\/[^\s]*)?/gi, '$1');

    // 6. Markdown headings, bold, italic, list bullets
    cleaned = cleaned
      .replace(/^#{1,6}\s+/gm, '')           // Headers #
      .replace(/\*\*([^*]+)\*\*/g, '$1')     // Bold **
      .replace(/\*([^*]+)\*/g, '$1')         // Italic *
      .replace(/__([^_]+)__/g, '$1')         // Underline __
      .replace(/^[-*+]\s+/gm, '')            // Unordered list bullets
      .replace(/^\d+\.\s+/gm, '')            // Numbered list items
      .replace(/^>\s+/gm, '')                // Blockquotes
      .replace(/---+|===+/g, '');            // Horizontal rules

    // 7. Markdown tables -> summary phrase
    cleaned = cleaned.replace(/\|.+\|\n\|[-:\s|]+\|\n(?:\|.+\|\n?)+/g, ' I have tabulated the details on screen. ');

    return cleaned;
  }

  /**
   * Expand abbreviations using regex word boundaries.
   */
  private static expandAbbreviations(text: string): string {
    let result = text;
    for (const [pattern, expansion] of Object.entries(SpeechPreparationService.ABBREVIATIONS)) {
      result = result.replace(new RegExp(pattern, 'g'), expansion);
    }
    return result;
  }

  /**
   * Detect whether text contains Tamil or Hindi characters or typical script.
   */
  public static detectScriptLanguage(text: string): string {
    // Tamil Unicode range: \u0B80-\u0BFF
    if (/[\u0B80-\u0BFF]/.test(text)) {
      return 'ta';
    }
    // Devanagari (Hindi) Unicode range: \u0900-\u097F
    if (/[\u0900-\u097F]/.test(text)) {
      return 'hi';
    }

    // Tanglish heuristics (common Tamil phonetics in Latin script)
    const lower = text.toLowerCase();
    const tanglishKeywords = ['vanakkam', 'epdi', 'irukku', 'irukkeenga', 'nalla', 'pannu', 'pannunga', 'ithu', 'adhu', 'theriyuma', 'sollu', 'sollunga', 'enakku', 'unakku', 'puriyala', 'romba'];
    if (tanglishKeywords.some(kw => new RegExp(`\\b${kw}\\b`).test(lower))) {
      return 'ta';
    }

    // Hinglish heuristics (common Hindi phonetics in Latin script)
    const hinglishKeywords = ['namaste', 'kaise', 'kya', 'samjhao', 'batao', 'theek', 'mera', 'aapka', 'accha', 'shukriya', 'karo', 'mujhe', 'hum', 'nahin', 'bhai'];
    if (hinglishKeywords.some(kw => new RegExp(`\\b${kw}\\b`).test(lower))) {
      return 'hi';
    }

    return 'en';
  }

  /**
   * Split continuous speech script into natural, breath-pause conversational segments
   * at punctuation boundaries (~60 to 140 chars per segment) for responsive streaming playback.
   */
  public static splitSpeechSegments(text: string): string[] {
    const rawChunks = text
      .split(/(?<=[.!?;\n])\s+/)
      .map(c => c.trim())
      .filter(c => c.length > 0);

    const segments: string[] = [];
    let currentBuffer = '';

    for (const chunk of rawChunks) {
      if ((currentBuffer + ' ' + chunk).trim().length <= 140) {
        currentBuffer = (currentBuffer + ' ' + chunk).trim();
      } else {
        if (currentBuffer) {
          segments.push(currentBuffer);
        }
        currentBuffer = chunk;
      }
    }

    if (currentBuffer) {
      segments.push(currentBuffer);
    }

    // If segments is still empty, fallback to single clean text
    return segments.length > 0 ? segments : [text.trim()];
  }

  /**
   * Master pipeline: Prepares raw AI response for both on-screen display and vocal synthesis.
   */
  public static formatResponse(rawText: string, forcedLanguage?: string): FormattedSpeechOutput {
    if (!rawText || !rawText.trim()) {
      return {
        displayText: '',
        speechText: '',
        speechChunks: [],
        detectedLanguage: forcedLanguage || 'en',
      };
    }

    // 1. Clean technical artifacts (code blocks, markdown, think tags)
    let speech = this.cleanTechnicalArtifacts(rawText);

    // 2. Normalize currencies & units
    speech = this.normalizeCurrency(speech);
    speech = this.normalizeUnits(speech);

    // 3. Expand technical abbreviations
    speech = this.expandAbbreviations(speech);

    // 4. Clean extra whitespaces, newlines, and trailing periods
    speech = speech
      .replace(/[\r\n]+/g, ' ')
      .replace(/\s{2,}/g, ' ')
      .trim();

    // 5. Detect language
    const detectedLang = forcedLanguage && forcedLanguage !== 'auto'
      ? forcedLanguage
      : this.detectScriptLanguage(rawText);

    // 6. Split into natural breath segments
    const speechChunks = this.splitSpeechSegments(speech);

    return {
      displayText: rawText.replace(/<think>[\s\S]*?<\/think>/gi, '').trim(),
      speechText: speech,
      speechChunks,
      detectedLanguage: detectedLang,
    };
  }
}

