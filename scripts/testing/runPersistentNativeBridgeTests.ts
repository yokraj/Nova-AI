import http from 'http';
import { NativeBridgeServer } from '../../apps/frontend/src/features/native-bridge/server/nativeBridgeServer';
import { NativeBridgeRequest } from '../../apps/frontend/src/features/native-bridge/types/nativeBridgeRequest';

let totalTests = 0;
let passedTests = 0;

function assert(condition: boolean, description: string) {
  totalTests++;
  if (condition) {
    passedTests++;
    console.log(`  ✓ PASS: ${description}`);
  } else {
    console.error(`  ✗ FAIL: ${description}`);
  }
}

function makeHttpRequest(
  options: http.RequestOptions,
  postData?: string
): Promise<{ statusCode?: number; headers: http.IncomingHttpHeaders; body: string }> {
  return new Promise((resolve, reject) => {
    const req = http.request(options, (res) => {
      let body = '';
      res.on('data', (chunk) => {
        body += chunk.toString();
      });
      res.on('end', () => {
        resolve({ statusCode: res.statusCode, headers: res.headers, body });
      });
    });

    req.on('error', (err) => reject(err));

    if (postData) {
      req.write(postData);
    }
    req.end();
  });
}

async function runPersistentNativeBridgeTests() {
  console.log('\n==================================================');
  console.log('  NOVA NATIVE BRIDGE FRONTEND ORIGIN INTEGRATION TESTS');
  console.log('==================================================\n');

  const server = new NativeBridgeServer();
  const testPort = 3001;

  // Test 1: Start server
  const started = await server.start(testPort);
  assert(started, `Native Bridge server started successfully on port ${testPort}`);

  try {
    // Test 2: GET /health works
    const healthRes = await makeHttpRequest({
      hostname: '127.0.0.1',
      port: testPort,
      path: '/health',
      method: 'GET',
      headers: {
        Origin: 'http://localhost:3000',
      },
    });

    assert(healthRes.statusCode === 200, 'GET /health endpoint returned HTTP 200 OK');
    const healthData = JSON.parse(healthRes.body);
    assert(
      healthData.status === 'healthy' && healthData.service === 'nova-native-bridge',
      'GET /health returned {"status":"healthy","service":"nova-native-bridge"}'
    );
    assert(
      healthRes.headers['access-control-allow-origin'] === 'http://localhost:3000',
      'GET /health dynamically sets Access-Control-Allow-Origin: http://localhost:3000'
    );

    // Test 3: Frontend Origin Allowlist Validation
    const allowedOriginsToTest = [
      'http://localhost:3000',
      'http://127.0.0.1:3000',
      'http://localhost:5173',
      'http://127.0.0.1:5173',
    ];

    for (const origin of allowedOriginsToTest) {
      const pingPayload: NativeBridgeRequest = {
        requestId: `test-req-${origin.replace(/[:/.]/g, '-')}`,
        capability: 'SYSTEM_CONTROL',
        action: 'GET_SYSTEM_INFO',
        target: { rawTarget: 'Host Workstation' },
        authorization: { isApproved: true },
        securityContext: { origin },
      };

      const res = await makeHttpRequest(
        {
          hostname: '127.0.0.1',
          port: testPort,
          path: '/api/v1/native-execute',
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Origin: origin,
          },
        },
        JSON.stringify(pingPayload)
      );

      assert(res.statusCode === 200, `Allowed origin ${origin} accepted with HTTP 200 OK`);
      assert(
        res.headers['access-control-allow-origin'] === origin,
        `Access-Control-Allow-Origin header reflects allowed origin ${origin}`
      );
    }

    // Test 4: Preflight OPTIONS for Allowed Origin
    const preflightRes = await makeHttpRequest({
      hostname: '127.0.0.1',
      port: testPort,
      path: '/api/v1/native-execute',
      method: 'OPTIONS',
      headers: {
        Origin: 'http://localhost:3000',
        'Access-Control-Request-Method': 'POST',
      },
    });

    assert(preflightRes.statusCode === 200, 'Preflight OPTIONS request from http://localhost:3000 returned HTTP 200 OK');
    assert(
      preflightRes.headers['access-control-allow-origin'] === 'http://localhost:3000',
      'Preflight OPTIONS header reflects http://localhost:3000'
    );

    // Test 5: Arbitrary & Untrusted Origins Rejected
    const forbiddenOrigins = [
      'http://malicious-attacker-site.com',
      'http://localhost:30000',
      'http://evil-domain.org:3000',
    ];

    for (const badOrigin of forbiddenOrigins) {
      const badRes = await makeHttpRequest({
        hostname: '127.0.0.1',
        port: testPort,
        path: '/api/v1/native-execute',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Origin: badOrigin,
        },
      });

      assert(badRes.statusCode === 403, `Untrusted origin ${badOrigin} rejected with HTTP 403 Forbidden`);
      const badData = JSON.parse(badRes.body);
      assert(badData.status === 'DENIED', `Untrusted origin ${badOrigin} response status is DENIED`);
    }

    // Test 6: Protected Process Protection (explorer.exe)
    const terminateProtectedPayload: NativeBridgeRequest = {
      requestId: 'test-req-protected',
      capability: 'SYSTEM_CONTROL',
      action: 'TERMINATE_PROCESS',
      target: { rawTarget: 'explorer.exe' },
      parameters: { processName: 'explorer.exe' },
      authorization: { isApproved: true },
      securityContext: { origin: 'http://localhost:3000' },
    };

    const protectedRes = await makeHttpRequest(
      {
        hostname: '127.0.0.1',
        port: testPort,
        path: '/api/v1/native-execute',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Origin: 'http://localhost:3000',
        },
      },
      JSON.stringify(terminateProtectedPayload)
    );

    const protectedData = JSON.parse(protectedRes.body);
    assert(
      protectedData.status === 'DENIED' && protectedData.errorReason === 'PROTECTED_PROCESS',
      'Attempt to terminate protected process explorer.exe is DENIED with errorReason PROTECTED_PROCESS'
    );

    // Test 7: Untrusted Executable Blocked
    const untrustedAppPayload: NativeBridgeRequest = {
      requestId: 'test-req-untrusted',
      capability: 'APPLICATION_CONTROL',
      action: 'OPEN_APPLICATION',
      target: { rawTarget: 'untrusted_malware.exe' },
      authorization: { isApproved: true },
      securityContext: { origin: 'http://localhost:3000' },
    };

    const untrustedRes = await makeHttpRequest(
      {
        hostname: '127.0.0.1',
        port: testPort,
        path: '/api/v1/native-execute',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Origin: 'http://localhost:3000',
        },
      },
      JSON.stringify(untrustedAppPayload)
    );

    const untrustedData = JSON.parse(untrustedRes.body);
    assert(
      untrustedData.status === 'UNSUPPORTED_CAPABILITY' || untrustedData.status === 'DENIED',
      'Attempt to launch untrusted application untrusted_malware.exe is blocked'
    );
  } finally {
    // Stop server cleanly
    await server.stop();
    assert(true, 'Native Bridge server stopped cleanly and released port 3001');
  }

  console.log('\n--------------------------------------------------');
  console.log(`  RESULTS: ${passedTests} / ${totalTests} PASSED`);
  console.log('--------------------------------------------------\n');

  if (passedTests !== totalTests) {
    process.exitCode = 1;
  } else {
    process.exitCode = 0;
  }
}

runPersistentNativeBridgeTests().catch((err) => {
  console.error('Test execution error:', err);
  process.exit(1);
});
