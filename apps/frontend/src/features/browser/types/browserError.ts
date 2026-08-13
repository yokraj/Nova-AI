export type BrowserErrorType =
  | 'INVALID_URL_SCHEME'
  | 'UNSAFE_DOMAIN_BLOCKED'
  | 'FORM_SUBMISSION_DENIED'
  | 'DOWNLOAD_PATH_TRAVERSAL'
  | 'ELEMENT_NOT_FOUND'
  | 'NAVIGATION_TIMEOUT'
  | 'SECURITY_APPROVAL_REQUIRED';

export interface BrowserError {
  type: BrowserErrorType;
  message: string;
  targetUrl?: string;
}
