import { runBrowserRuntimeTests } from '../src/features/browser/tests/browserRuntime.test.js';

async function main() {
  console.log('=== NOVA BROWSER CAPABILITY TEST SUITE ===\n');

  const res = await runBrowserRuntimeTests();
  res.results.forEach((r) => console.log('   ', r));

  console.log('\n======================================');
  console.log(`OVERALL BROWSER TEST RESULT: ${res.passed ? 'PASSED' : 'FAILED'}`);
  console.log('======================================');

  if (!res.passed) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Test runner failed:', err);
  process.exit(1);
});
