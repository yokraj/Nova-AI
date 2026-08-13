# Nova AI Enterprise Security Guide & Hardening Manual

## Executive Summary
This document provides complete documentation of security controls, threat protection, audit logging, RBAC authorization, session management, rate limiting, and compliance specifications implemented in the **Nova AI Enterprise Dashboard Backend**.

---

## 1. Authentication & RBAC Authorization

### JWT Token Verification
All REST endpoints and WebSocket handshakes enforce strict Bearer Token verification integrated with `app.identity.infrastructure.rbac`. Tokens are decoded using HMAC-SHA256 or RSA-256 signatures, checking expiration (`exp`), issuer (`iss`), and subject claims (`sub`).

### Permission Scopes Matrix

| Role | Scope Permissions | Access Level |
| :--- | :--- | :--- |
| **`admin`** | `dashboard:read`, `dashboard:write`, `dashboard:admin` | Full read, write, system config & session revocation control |
| **`user`** | `dashboard:read`, `dashboard:write` | Read telemetry, manage personal dashboard settings & acknowledge alerts |
| **`viewer`** | `dashboard:read` | Read-only access to overview, telemetry, and health metrics |

---

## 2. Sliding Window Rate Limiting

The `DashboardRateLimiter` enforces request rate bounds using sliding window timestamp tracking:

- **Standard API Rate**: `120 requests / minute` per client IP.
- **Burst Capacity**: `20 requests / burst window`.
- **Exceeded Threshold Response**: HTTP `429 Too Many Requests` with `Retry-After: 60`.

---

## 3. Session Revocation & Management

The `DashboardSessionManager` provides active session tracking and instant revocation:
- **Session Expiration**: Automatic TTL invalidation after `3600 seconds` (1 hour) of inactivity.
- **Instant Revocation**: Admins can invoke `terminate_user_sessions(user_id)` or `revoke_session(token)` to instantly invalidate compromised tokens across REST and active WebSocket connections.

---

## 4. WebSocket Anti-Abuse & Frame Security

The `WebSocketSecurityManager` enforces real-time socket anti-abuse bounds:
1. **Frame Payload Restriction**: Rejects frames exceeding `64 KB` (`65,536 bytes`) with `WebSocketSecurityException`.
2. **IP Connection Bounds**: Caps max simultaneous connections to `10 sockets per client IP`.
3. **Spam & Flood Throttling**: Flags connections transmitting > `20 messages per 5-second window`, dropping spam frames.

---

## 5. Threat Intrusion Detection

The `ThreatDetector` analyzes structural telemetry and access logs in real-time to trigger security alerts:

- **Brute-Force Detection**: Triggers `BRUTE_FORCE_ATTEMPT` alert when 5 failed login attempts originate from a single IP within 300s.
- **Token Abuse Detection**: Flags rapid access attempts using revoked or invalid JWTs (`INVALID_TOKEN_ATTEMPT`).
- **Permission Scanning**: Flags attempts by unauthorized roles to probe `dashboard:admin` endpoints (`PERMISSION_ESCALATION_ATTEMPT`).

---

## 6. Audit Logging & Compliance

All security alerts, permission checks, and threat events emit structured JSON logs via `AuditLogger`:

```json
{
  "timestamp": "2026-08-02T22:30:00Z",
  "event_id": "9b12c345-6789-4def-0123-456789abcdef",
  "action": "threat_BRUTE_FORCE_ATTEMPT",
  "user_id": "target_admin",
  "role": "unknown",
  "ip_address": "192.168.1.99",
  "endpoint": "security_monitor",
  "resource": "threat_detector",
  "result": "alert",
  "metadata": { "failed_login_count": 5 }
}
```

The `ComplianceManager` produces automated reports for standard enterprise frameworks:
- **SOC 2 Type II Compliance**: Access control, audit trail logging, and session encryption.
- **ISO 27001 Compliance**: Information security asset risk scoring.
- **GDPR Compliance**: Data minimization and audit logging of PII queries.

---

## 7. Security Hardening Headers

The `DashboardSecurityMiddleware` injects strict security headers into every HTTP response:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; frame-ancestors 'none';
Cache-Control: no-store, max-age=0
```
