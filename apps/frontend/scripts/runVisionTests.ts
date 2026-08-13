import { runVisionRuntimeTests } from '../src/features/vision/tests/visionRuntime.test.js';

async function main() {
  console.log('=== NOVA VISION CAPABILITY TEST SUITE ===\n');

  const res = await runVisionRuntimeTests();
  res.results.forEach((r) => console.log('   ', r));

  console.log('\n======================================');
  console.log(`OVERALL VISION TEST RESULT: ${res.passed ? 'PASSED' : 'FAILED'}`);
  console.log('======================================');

  if (!res.passed) {
    process.exit(1);
  }
}

main().catch((err) => {
  console.error('Test runner failed:', err);
  process.exit(1);
});
