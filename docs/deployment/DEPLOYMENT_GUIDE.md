# Nova AI Enterprise Dashboard Deployment Guide

## Executive Overview
This document provides production deployment procedures, environment configuration, Docker containerization setups, NGINX reverse proxy configs, SSL/TLS termination, database backup strategies, and scaling guidelines for the **Nova AI Enterprise Dashboard Backend**.

---

## 1. System Requirements & Prerequisites

- **Operating System**: Linux (Ubuntu 22.04 LTS / RHEL 9 recommended) or Windows Server 2022
- **Python Runtime**: Python `3.11+` or `3.14+`
- **CPU / RAM Minimum**: 2 vCPU, 4 GB RAM (Recommended: 4 vCPU, 8 GB RAM)
- **Database**: PostgreSQL `15+` (or SQLite for dev/single-node deployment)
- **In-Memory Cache**: Redis `7.0+` (optional, in-memory fallback enabled by default)

---

## 2. Environment Configuration (`.env`)

Copy `.env.example` to `.env` and set production environment variables:

```ini
# Core Server Configuration
NOVA_ENV=production
NOVA_HOST=0.0.0.0
NOVA_PORT=8000
NOVA_LOG_LEVEL=INFO

# Security & Secrets
JWT_SECRET_KEY=e9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8
JWT_ALGORITHM=HS256
CORS_ALLOWED_ORIGINS=https://dashboard.nova-ai.internal

# Database Persistence
DATABASE_URL=postgresql+asyncpg://nova_user:SuperSecretPass123!@localhost:5432/nova_db
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Monitoring & Analytics Engine Limits
METRICS_INTERVAL=10
SNAPSHOT_RETENTION=50
ANALYTICS_RETENTION_DAYS=90
```

---

## 3. Docker Containerization

### A. Dockerfile (`apps/backend/Dockerfile`)
```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### B. Docker Compose (`docker-compose.yml`)
```yaml
version: '3.8'

services:
  nova-backend:
    build:
      context: ./apps/backend
      dockerfile: Dockerfile
    container_name: nova_dashboard_backend
    restart: always
    ports:
      - "8000:8000"
    environment:
      - NOVA_ENV=production
      - DATABASE_URL=postgresql+asyncpg://nova_user:SuperSecretPass123!@postgres:5432/nova_db
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15-alpine
    container_name: nova_postgres
    restart: always
    environment:
      POSTGRES_USER: nova_user
      POSTGRES_PASSWORD: SuperSecretPass123!
      POSTGRES_DB: nova_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: nova_redis
    restart: always

volumes:
  postgres_data:
```

---

## 4. Reverse Proxy & SSL/TLS Setup (NGINX)

Configure NGINX as an HTTPS reverse proxy with WebSocket upgrade support:

```nginx
server {
    listen 443 ssl http2;
    server_name dashboard.nova-ai.internal;

    ssl_certificate /etc/letsencrypt/live/dashboard.nova-ai.internal/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dashboard.nova-ai.internal/privkey.pem;

    # REST API Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket Gateway Proxy
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400s;
        proxy_send_timeout 86400s;
    }
}
```

---

## 5. Database Backup & Disaster Recovery

### Automated Daily Backup Script (`scripts/backup_db.sh`):
```bash
#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/var/backups/nova_db"
mkdir -p $BACKUP_DIR

pg_dump -U nova_user -h localhost -d nova_db | gzip > "$BACKUP_DIR/nova_db_$TIMESTAMP.sql.gz"
find $BACKUP_DIR -type f -mtime +30 -name "*.sql.gz" -delete
```

### Restore Procedure:
```bash
gunzip -c /var/backups/nova_db/nova_db_20260802_220000.sql.gz | psql -U nova_user -d nova_db
```
