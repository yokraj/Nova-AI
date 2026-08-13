import { PathResolver } from '../resolvers/pathResolver';
import { PathSecurity } from '../security/pathSecurity';
import { FileSystemPolicy } from '../security/filesystemPolicy';
import { WindowsFileSystemAdapter } from '../adapters/windowsFileSystemAdapter';
import { ExecutionRequest } from '@/features/execution-runtime/types/executionRequest';

export async function runFileSystemRuntimeTests(): Promise<{ passed: boolean; results: string[] }> {
  const pathResolver = new PathResolver();
  const pathSecurity = new PathSecurity();
  const policy = new FileSystemPolicy();
  const adapter = new WindowsFileSystemAdapter();
  const results: string[] = [];
  let allPassed = true;

  const logResult = (testName: string, success: boolean, detail: string) => {
    const msg = `[${success ? 'PASS' : 'FAIL'}] ${testName}: ${detail}`;
    results.push(msg);
    if (!success) allPassed = false;
  };

  // Test 1: Special Folder Resolution ("Desktop", "Downloads")
  const pDesktop = pathResolver.resolve('Desktop');
  logResult('Special Folder Resolution (Desktop)', pDesktop.endsWith('/Desktop'), `Resolved path: ${pDesktop}`);

  // Test 2: Phrase Natural Resolution ("Projects on my Desktop")
  const pProj = pathResolver.resolve('Projects on my Desktop');
  logResult('Natural Phrase Resolution', pProj.endsWith('/Desktop/Projects'), `Resolved path: ${pProj}`);

  // Test 3: Path Traversal Protection Rejection
  const sTrav = pathSecurity.isSafePath('../../../Windows/System32');
  logResult('Path Traversal Protection Rejection', !sTrav.safe, `Blocked traversal: ${sTrav.reason}`);

  // Test 4: Protected System Directory Protection
  const sWin = pathSecurity.isSafePath('C:/Windows/System32/cmd.exe');
  logResult('Protected System Location Protection', !sWin.safe, `Blocked access: ${sWin.reason}`);

  // Test 5: Directory Creation & Verification
  const reqCreateDir: ExecutionRequest = {
    executionId: 'exec-cd-01',
    commandId: 'cmd-cd-01',
    capability: 'FILE_SYSTEM',
    action: 'CREATE_DIRECTORY',
    target: 'TestProjects on my Desktop',
    requestedBy: 'user',
    workspace: 'default',
    riskLevel: 'LOW',
    policy: 'ALLOW',
    permissions: [],
    timestamp: new Date().toISOString(),
  };

  const resCreateDir = await adapter.execute(reqCreateDir);
  logResult(
    'Directory Creation & Verification',
    resCreateDir.status === 'COMPLETED' && resCreateDir.verification === 'STATE_VERIFIED',
    `Status: ${resCreateDir.status}, Verification: ${resCreateDir.verification}`
  );

  // Test 6: File Creation & Write Verification
  const reqCreateFile: ExecutionRequest = {
    executionId: 'exec-cf-01',
    commandId: 'cmd-cf-01',
    capability: 'FILE_SYSTEM',
    action: 'CREATE_FILE',
    target: 'notes.txt in Downloads',
    parameters: { content: 'Nova AI Test Notes Content' },
    requestedBy: 'user',
    workspace: 'default',
    riskLevel: 'LOW',
    policy: 'ALLOW',
    permissions: [],
    timestamp: new Date().toISOString(),
  };

  const resCreateFile = await adapter.execute(reqCreateFile);
  logResult(
    'File Creation & Write Verification',
    resCreateFile.status === 'COMPLETED' && resCreateFile.verification === 'STATE_VERIFIED',
    `Status: ${resCreateFile.status}, Size: ${resCreateFile.metadata?.sizeBytes} bytes`
  );

  // Test 7: File Search & Structured Listing
  const reqSearch: ExecutionRequest = {
    executionId: 'exec-sr-01',
    commandId: 'cmd-sr-01',
    capability: 'FILE_SYSTEM',
    action: 'SEARCH_FILES',
    target: 'Downloads',
    parameters: { extension: 'txt' },
    requestedBy: 'user',
    workspace: 'default',
    riskLevel: 'SAFE',
    policy: 'ALLOW',
    permissions: [],
    timestamp: new Date().toISOString(),
  };

  const resSearch = await adapter.execute(reqSearch);
  const items = resSearch.metadata?.itemsFound || [];
  logResult(
    'File Search & Structured Listing',
    resSearch.status === 'COMPLETED' && items.length > 0,
    `Found ${items.length} items matching filter`
  );

  // Test 8: Destructive Operation Policy & Approval Trigger
  const isDestructiveApproval = policy.requiresApproval('DELETE_DIRECTORY');
  logResult('Destructive Operation Policy Approval Trigger', isDestructiveApproval, 'DELETE_DIRECTORY requires approval');

  return { passed: allPassed, results };
}
