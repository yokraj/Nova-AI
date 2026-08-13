import { runNativeBridgeUnitTests } from '../src/features/native-bridge/tests/nativeBridgeRuntime.test.js';
import { runRealWindowsSmokeTests } from '../src/features/native-bridge/tests/realSmokeTest.js';

async function main() {
  console.log('=== NOVA NATIVE BRIDGE TEST SUITE ===\n');

  console.log('1. Running Unit Tests...');
  const unitRes = await runNativeBridgeUnitTests();
  unitRes.results.forEach((r) => console.log('   ', r));

  console.log('\n2. Running Real Windows End-to-End Smoke Tests...');
  const smokeRes = await runRealWindowsSmokeTests();
  smokeRes.results.forEach((r) => console.log('   ', r));

  const totalPassed = unitRes.passed && smokeRes.passed;
  console.log('\n======================================');
  console.log(`OVERALL NATIVE BRIDGE TEST RESULT: ${totalPassed ? 'PASSED' : 'FAILED'}`);
  console.log('======================================');

  if (!totalPassed) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Test runner failed:', err);
  process.exit(1);
});
