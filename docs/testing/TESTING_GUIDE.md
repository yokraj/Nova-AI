# Nova AI Enterprise Dashboard Testing Guide

## Executive Summary
This guide outlines the testing philosophy, test suite organization, quality gates, coverage requirements, and execution instructions for the **Nova AI Enterprise Dashboard Backend**.

---

## 1. Test Suite Architecture

Tests are located in `apps/backend/tests/` and structured into 7 distinct suites:

```text
apps/backend/tests/
├── fixtures/                      # Shared mock context & telemetry data generators
│   └── dashboard_fixtures.py
├── unit/                          # Unit tests for isolated service/engine components
│   ├── test_analytics_engine.py
│   └── test_dashboard_security.py
├── integration/                   # End-to-end telemetry pipeline integration tests
│   └── test_dashboard_integration.py
├── performance/                   # Latency, throughput & downsampling profiling
│   └── test_dashboard_performance.py
├── load/                          # Concurrent WebSocket & API load simulation
│   └── test_dashboard_load.py
├── stress/                        # Queue saturation & memory eviction under stress
│   └── test_dashboard_stress.py
├── security/                      # RBAC, brute-force alerts & anti-spam validation
│   └── test_dashboard_security_hardening.py
├── chaos/                         # Disconnects & hardware collector failure fallbacks
│   └── test_dashboard_chaos.py
└── reports/                       # Master automated test suite runner
    └── test_suite_runner.py
```

---

## 2. Running Test Suites

### A. Run Master Test Suite Runner (All 14 Enterprise Suites)
```bash
cd apps/backend
py tests/reports/test_suite_runner.py
```

### B. Run Pytest Unit & Integration Tests with Coverage
```bash
cd apps/backend
py -m pytest tests/ --cov=app --cov-report=term-missing
```

### C. Run Specific Test Category
```bash
# Run Load Tests
py -m pytest tests/load/test_dashboard_load.py

# Run Security Tests
py -m pytest tests/security/test_dashboard_security_hardening.py
```

---

## 3. Quality Gates & Coverage Requirements

- **Overall Core Backend Coverage**: Must exceed **95%**.
- **REST API Success Rate**: Must meet or exceed **99.9%**.
- **WebSocket Broadcast Stability**: Must meet or exceed **99.9%**.
- **Notification Queue Delivery Rate**: Must meet or exceed **99.9%**.
- **Zero Memory Leaks**: In-memory ring buffers must remain bounded under maximum stress.
