export type BrowserVerificationState =
  | 'VERIFIED'
  | 'URL_MATCHED'
  | 'ELEMENT_FOUND'
  | 'CONTENT_EXTRACTED'
  | 'FILE_DOWNLOADED'
  | 'SCREENSHOT_TAKEN'
  | 'UNVERIFIED'
  | 'VERIFICATION_FAILED';

export interface ExtractedWebLink {
  text: string;
  url: string;
}

export interface BrowserResult {
  requestId: string;
  success: boolean;
  status:
    | 'COMPLETED'
    | 'FAILED'
    | 'DENIED'
    | 'AWAITING_APPROVAL'
    | 'TIMED_OUT'
    | 'VERIFICATION_FAILED';
  action: string;
  targetUrl?: string;
  verification: BrowserVerificationState;
  message: string;
  durationSeconds: number;
  extractedText?: string;
  extractedLinks?: ExtractedWebLink[];
  screenshotBase64?: string;
  downloadedFilePath?: string;
  isSimulated?: boolean;
  errorReason?: string;
  timestamp: string;
}
