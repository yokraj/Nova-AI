export type TabStatus = 'LOADING' | 'READY' | 'ERROR';

export interface BrowserTab {
  id: string;
  browserId: string;
  title: string;
  url: string;
  domain: string;
  status: TabStatus;
  active: boolean;
  favIconUrl?: string;
}
