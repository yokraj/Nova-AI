import { UrlResolver } from '../resolvers/urlResolver';
import { NavigationGuard } from '../security/navigationGuard';
import { DownloadGuard } from '../security/downloadGuard';
import { FormSubmissionGuard } from '../security/formSubmissionGuard';
import { BrowserPolicy } from '../security/browserPolicy';
import { DomainPolicy } from '../security/domainPolicy';
import { NativeBrowserAdapter } from '../adapters/nativeBrowserAdapter';
import { BrowserRequest } from '../types/browserRequest';

export async function runBrowserRuntimeTests(): Promise<{ passed: boolean; results: string[] }> {
  const urlResolver = new UrlResolver();
  const navGuard = new NavigationGuard();
  const downloadGuard = new DownloadGuard();
  const formGuard = new FormSubmissionGuard();
  const browserPolicy = new BrowserPolicy();
  const domainPolicy = new DomainPolicy();
  const adapter = new NativeBrowserAdapter();

  const results: string[] = [];
  let allPassed = true;

  const logResult = (testName: string, success: boolean, detail: string) => {
    const msg = `[${success ? 'PASS' : 'FAIL'}] BROWSER UNIT TEST: ${testName} - ${detail}`;
    results.push(msg);
    if (!success) allPassed = false;
  };

  // Test 1: URL Resolution & Normalization ("open Google")
  const urlGoogle = urlResolver.resolveUrl('open Google');
  logResult('URL Resolution (open Google)', urlGoogle.valid && urlGoogle.resolvedUrl === 'https://www.google.com', `Resolved: ${urlGoogle.resolvedUrl}`);

  // Test 2: HTTPS Normalization for plain domains ("example.com")
  const urlEx = urlResolver.resolveUrl('example.com');
  logResult('HTTPS Normalization', urlEx.valid && urlEx.resolvedUrl === 'https://example.com/', `Resolved: ${urlEx.resolvedUrl}`);

  // Test 3: Disallowed Scheme Rejection (javascript:alert(1))
  const navJs = navGuard.validateNavigation('javascript:alert(1)');
  logResult('Disallowed Scheme Rejection (javascript:)', !navJs.safe, `Blocked: ${navJs.reason}`);

  // Test 4: File Scheme Rejection (file:///C:/Windows)
  const navFile = navGuard.validateNavigation('file:///C:/Windows/System32');
  logResult('Disallowed Scheme Rejection (file:)', !navFile.safe, `Blocked: ${navFile.reason}`);

  // Test 5: Safe Navigation Policy Assessment
  const riskNav = browserPolicy.getRiskLevel('NAVIGATE');
  logResult('Safe Navigation Policy', riskNav === 'SAFE', `Risk level: ${riskNav}`);

  // Test 6: Form Submission Risk & Approval Requirement
  const formRisk = formGuard.assessFormAction('submit form', 'Submit Application');
  logResult('Form Submission Approval Requirement', formRisk.requiresApproval && formRisk.riskLevel === 'HIGH', `Risk: ${formRisk.riskLevel}`);

  // Test 7: Download Security & Path Security
  const dlCheck = downloadGuard.validateDownload('https://example.com/file.pdf', 'C:/Users/DefaultUser/Downloads/file.pdf');
  logResult('Download Security Check', dlCheck.safe, 'Valid HTTPS download path accepted');

  // Test 8: Download Path Traversal Protection
  const dlTrav = downloadGuard.validateDownload('https://example.com/file.pdf', 'C:/Users/DefaultUser/Downloads/../../Windows/System32/file.dll');
  logResult('Download Path Traversal Protection', !dlTrav.safe, `Blocked: ${dlTrav.reason}`);

  // Test 9: Domain Trust Policy (github.com)
  const domGithub = domainPolicy.isTrustedDomain('github.com');
  logResult('Domain Trust Policy (github.com)', domGithub, 'github.com recognized as trusted domain');

  // Test 10: Mock Fallback Execution & Truthful Verification State
  const req: BrowserRequest = {
    requestId: 'test-req-01',
    action: 'NAVIGATE',
    target: { rawTarget: 'open Google', url: 'https://www.google.com', domain: 'google.com' },
    riskLevel: 'SAFE',
    requiresApproval: false,
    timestamp: new Date().toISOString(),
  };

  const res = await adapter.execute(req);
  logResult(
    'Mock Fallback & Truthful Verification',
    res.success && res.verification === 'URL_MATCHED',
    `Status: ${res.status}, Verification: ${res.verification}, Simulated: ${res.isSimulated}`
  );

  return { passed: allPassed, results };
}
