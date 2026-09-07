import { NativeBridgeServer } from '../src/features/native-bridge/server/nativeBridgeServer';

async function main() {
  const server = new NativeBridgeServer();
  const port = 3001;

  const started = await server.start(port);

  if (!started) {
    console.error(`Failed to start Nova Native Bridge on port ${port}. Port may already be in use.`);
    process.exit(1);
  }

  console.log('==================================================');
  console.log('NOVA NATIVE BRIDGE');
  console.log('Status: RUNNING');
  console.log('Host: 127.0.0.1');
  console.log(`Port: ${port}`);
  console.log('==================================================');

  const shutdown = async (signal: string) => {
    console.log(`\nReceived ${signal}. Shutting down Nova Native Bridge...`);
    await server.stop();
    console.log('Nova Native Bridge stopped cleanly.');
    process.exit(0);
  };

  process.on('SIGINT', () => shutdown('SIGINT'));
  process.on('SIGTERM', () => shutdown('SIGTERM'));

  // Keep event loop alive
  setInterval(() => {}, 60000);
}

main().catch((err) => {
  console.error('Unhandled Native Bridge Server error:', err);
  process.exit(1);
});
