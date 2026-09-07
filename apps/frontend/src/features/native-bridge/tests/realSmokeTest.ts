import fs from 'fs';
import path from 'path';
import { NativeBridgeServer } from '../server/nativeBridgeServer';
import { NativeBridgeClient } from '../client/nativeBridgeClient';
import { NativeBridgeRequest } from '../types/nativeBridgeRequest';

export async function runRealWindowsSmokeTests(): Promise<{ passed: boolean; results: string[] }> {
  const server = new NativeBridgeServer();
  const client = new NativeBridgeClient();
  const results: string[] = [];
  let allPassed = true;

  const logResult = (testName: string, success: boolean, detail: string) => {
    const msg = `[${success ? 'PASS' : 'FAIL'}] REAL SMOKE TEST: ${testName} - ${detail}`;
    results.push(msg);
    if (!success) allPassed = false;
  };

  // Safe isolated sandbox directory inside Nova project
  const sandboxDir = path.resolve('c:/Projects/Nova-AI/apps/frontend/.nova_test_sandbox');

  try {
    // Start local Native Bridge server on port 3001
    let started = await server.start(3001);
    if (!started) {
      const health = await client.healthCheck();
      started = health.healthy;
    }
    logResult('Native Bridge Server Start', started, 'Server bound to 127.0.0.1:3001');

    if (!started) {
      return { passed: false, results };
    }


    // Test 1: Real Directory Creation on Windows Filesystem
    const reqCreateDir: NativeBridgeRequest = {
      requestId: 'smoke-dir-01',
      capability: 'FILE_SYSTEM',
      action: 'CREATE_DIRECTORY',
      target: { rawTarget: sandboxDir, resolvedPath: sandboxDir },
      authorization: { userId: 'smoke-user', sessionToken: 'token', riskLevel: 'LOW', isApproved: true },
      timestamp: new Date().toISOString(),
    };

    const resCreateDir = await client.executeNative(reqCreateDir);
    const realDirExists = fs.existsSync(sandboxDir) && fs.statSync(sandboxDir).isDirectory();
    logResult('Real Directory Creation', resCreateDir.status === 'COMPLETED' && realDirExists, `Path: ${sandboxDir}`);

    // Test 2: Real Text File Creation & Write Content on Disk
    const testFilePath = path.join(sandboxDir, 'smoke_test.txt');
    const reqCreateFile: NativeBridgeRequest = {
      requestId: 'smoke-file-01',
      capability: 'FILE_SYSTEM',
      action: 'WRITE_TEXT_FILE',
      target: { rawTarget: testFilePath, resolvedPath: testFilePath },
      parameters: { contentPayload: 'Hello Nova AI Real Windows Execution Bridge!' },
      authorization: { userId: 'smoke-user', sessionToken: 'token', riskLevel: 'LOW', isApproved: true },
      timestamp: new Date().toISOString(),
    };

    const resCreateFile = await client.executeNative(reqCreateFile);
    const realFileExists = fs.existsSync(testFilePath);
    logResult('Real File Creation', resCreateFile.status === 'COMPLETED' && realFileExists, `Path: ${testFilePath}`);

    // Test 3: Real File Content Read & Verification from Disk
    const reqReadFile: NativeBridgeRequest = {
      requestId: 'smoke-read-01',
      capability: 'FILE_SYSTEM',
      action: 'READ_TEXT_FILE',
      target: { rawTarget: testFilePath, resolvedPath: testFilePath },
      authorization: { userId: 'smoke-user', sessionToken: 'token', riskLevel: 'SAFE', isApproved: true },
      timestamp: new Date().toISOString(),
    };

    const resReadFile = await client.executeNative(reqReadFile);
    const contentMatches = resReadFile.resultData?.contentOutput === 'Hello Nova AI Real Windows Execution Bridge!';
    logResult('Real File Content Verification', resReadFile.status === 'COMPLETED' && contentMatches, 'Content verified');

    // Test 4: Real File Rename on Disk
    const renamedFilePath = path.join(sandboxDir, 'smoke_test_renamed.txt');
    const reqRename: NativeBridgeRequest = {
      requestId: 'smoke-rename-01',
      capability: 'FILE_SYSTEM',
      action: 'RENAME_FILE',
      target: { rawTarget: testFilePath, resolvedPath: testFilePath },
      parameters: { destinationPath: renamedFilePath },
      authorization: { userId: 'smoke-user', sessionToken: 'token', riskLevel: 'LOW', isApproved: true },
      timestamp: new Date().toISOString(),
    };

    const resRename = await client.executeNative(reqRename);
    const oldAbsent = !fs.existsSync(testFilePath);
    const newExists = fs.existsSync(renamedFilePath);
    logResult('Real File Rename', resRename.status === 'COMPLETED' && oldAbsent && newExists, 'Old file absent, renamed file present');

    // Test 5: Real File Deletion from Disk
    const reqDeleteFile: NativeBridgeRequest = {
      requestId: 'smoke-del-01',
      capability: 'FILE_SYSTEM',
      action: 'DELETE_FILE',
      target: { rawTarget: renamedFilePath, resolvedPath: renamedFilePath },
      authorization: { userId: 'smoke-user', sessionToken: 'token', riskLevel: 'HIGH', isApproved: true },
      timestamp: new Date().toISOString(),
    };

    const resDeleteFile = await client.executeNative(reqDeleteFile);
    const fileGone = !fs.existsSync(renamedFilePath);
    logResult('Real File Deletion', resDeleteFile.status === 'COMPLETED' && fileGone, 'File removed from Windows disk');

    // Test 6: Real Windows Application Process Check / Resolution
    const reqApp: NativeBridgeRequest = {
      requestId: 'smoke-app-01',
      capability: 'APPLICATION_CONTROL',
      action: 'VERIFY_APPLICATION_RUNNING',
      target: { rawTarget: 'VS Code', applicationAlias: 'VS Code' },
      authorization: { userId: 'smoke-user', sessionToken: 'token', riskLevel: 'SAFE', isApproved: true },
      timestamp: new Date().toISOString(),
    };

    const resApp = await client.executeNative(reqApp);
    logResult('Application Control Process Check', resApp.status === 'COMPLETED', `Process status checked (${resApp.verification})`);

    // Clean up temporary sandbox directory
    if (fs.existsSync(sandboxDir)) {
      fs.rmSync(sandboxDir, { recursive: true, force: true });
    }
    logResult('Test Sandbox Cleanup', !fs.existsSync(sandboxDir), 'Temporary sandbox directory removed');
  } catch (err: any) {
    logResult('Smoke Test Execution Error', false, err?.message || 'Unknown error');
  } finally {
    await server.stop();
  }

  return { passed: allPassed, results };
}
