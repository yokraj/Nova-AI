# Nova AI Enterprise WebSocket Gateway Protocol Specification

## Protocol Overview
The Enterprise WebSocket Gateway provides authenticated, bidirectional, real-time event streaming between backend services and connected React dashboard clients.

- **WebSocket Endpoint**: `ws://<host>:<port>/ws/dashboard` (or `wss://` in production)
- **Subprotocol**: `json`
- **Max Frame Size**: 64 KB (`65,536 bytes`)
- **Max IP Connections**: 10 active connections per client IP

---

## 1. Connection Handshake & Authentication

### Handshake Parameters
Clients authenticate during socket initiation by providing a JWT token via query parameter or header:
`ws://localhost:8000/ws/dashboard?token=<JWT_TOKEN>`

### Authentication Ack Frame
Upon successful handshake, the Gateway returns a `connection_ack` frame:
```json
{
  "event": "connection_ack",
  "channel": "system",
  "payload": {
    "connection_id": "87ae7842-69e4-45ed-bc13-4e45e47fc954",
    "user_id": "usr-8812",
    "status": "connected"
  },
  "timestamp": "2026-08-02T22:30:00Z"
}
```

---

## 2. Standard Envelope Message Format

All incoming and outgoing frames conform to the `WebSocketMessage` JSON schema:

```json
{
  "event": "<event_type_identifier>",
  "channel": "<target_channel_topic>",
  "payload": { ... },
  "timestamp": "<iso_8601_utc_timestamp>"
}
```

---

## 3. Supported Channel Topics & Events

| Channel Topic | Event Identifier | Description |
| :--- | :--- | :--- |
| `dashboard` | `dashboard.snapshot.created` | Full consolidated dashboard state snapshot. |
| `resources` | `resource.updated` | Hardware resources delta update (CPU, RAM, Disk, Net, GPU). |
| `cpu` | `cpu.updated` | Detailed CPU core breakdown and temperature metrics. |
| `memory` | `memory.updated` | RAM and swap space utilization deltas. |
| `disk` | `disk.updated` | Disk partitions, I/O rates, and space utilization. |
| `network` | `network.updated` | Network Interface Card rx/tx byte rates. |
| `gpu` | `gpu.updated` | NVIDIA GPU temperature, VRAM, and compute utilization. |
| `processes` | `process.updated` | Top CPU & memory consuming process list. |
| `notifications` | `notification.created` | High-priority system alert or threshold warning. |
| `health` | `health.updated` | Subsystem diagnostic health state transitions. |

---

## 4. Client Channel Subscription Control

Clients manage topic subscriptions by sending `subscribe` or `unsubscribe` control frames:

### Subscribe Frame:
```json
{
  "event": "subscribe",
  "channel": "resources",
  "payload": { "channel": "resources" }
}
```

### Unsubscribe Frame:
```json
{
  "event": "unsubscribe",
  "channel": "resources",
  "payload": { "channel": "resources" }
}
```

---

## 5. Heartbeat & Ping-Pong Keepalive

- **Heartbeat Interval**: 30 seconds (`heartbeat_interval=30.0`).
- **Ping Frame**: Server transmits `{"event": "ping"}` frame every 30s.
- **Pong Response**: Client must reply with `{"event": "pong"}` within 10 seconds.
- **Stale Connection Pruning**: Sockets failing to return pong responses within 2 missed intervals are automatically terminated and deregistered.

---

## 6. Client Reconnect Strategy

Clients experiencing abrupt socket drops should implement an Exponential Backoff Reconnection algorithm:
- **Base Interval**: 1,000 ms (1 sec)
- **Backoff Multiplier**: 2.0
- **Max Delay**: 30,000 ms (30 sec)
- **Jitter**: ± 20% random variation to avoid thundering herd reconnection storms.

---

## 7. Error Frames Reference

If a client sends invalid JSON, requests forbidden channels, or violates rate limits:

```json
{
  "event": "error",
  "channel": "system",
  "payload": {
    "error_code": "SPAM_FLOOD_DETECTED",
    "message": "Message rate exceeds 20 frames per 5-second window"
  },
  "timestamp": "2026-08-02T22:30:00Z"
}
```
