# Backend and Database Roadmap

This document defines a practical migration path from the current local Web Serial dashboard to a persistent backend architecture.

## Goals

1. Persist telemetry history.
2. Support stable real-time UI without direct serial dependency.
3. Enable remote access and multi-client dashboards.
4. Improve observability and long-term reliability.

## Proposed Target Architecture

Data flow:

1. ESP sender transmits to ESP receiver via ESP-NOW.
2. Receiver outputs NDJSON over USB serial.
3. PC collector service reads serial, validates, and stores telemetry in DB.
4. API service exposes latest/history/aggregates.
5. Web dashboard fetches data from API (and optional WebSocket stream).

## Suggested Tech Stack

Minimal first step:

- Collector + API: Python FastAPI service
- Database: PostgreSQL
- Frontend: existing `web/` app migrated from Web Serial to HTTP/WebSocket

Alternative:

- Node.js Express collector/API + PostgreSQL

## Data Model

Table: `telemetry_readings`

- `id` BIGSERIAL PRIMARY KEY
- `receiver_mac` TEXT NOT NULL
- `sender_mac` TEXT NOT NULL
- `sequence` BIGINT NOT NULL
- `temperature` REAL NOT NULL
- `ph` REAL NOT NULL
- `flow` REAL NOT NULL
- `turbidity` REAL NOT NULL
- `tds` REAL NOT NULL
- `sender_uptime_ms` BIGINT
- `received_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

Indexes and constraints:

1. UNIQUE (`receiver_mac`, `sender_mac`, `sequence`) to prevent duplicate inserts.
2. INDEX on `received_at` for time queries.
3. INDEX on (`sender_mac`, `received_at`) for per-device history.

Optional table: `receiver_stats_snapshots`

- `received_at`
- `total`
- `valid`
- `invalid`
- `dropped`
- `sequence_gaps`
- `queue_depth`

## API Contract (Initial)

1. `GET /api/health`
- Returns service and DB health.

2. `GET /api/latest`
- Latest telemetry row (or latest per sender).

3. `GET /api/history?from=&to=&limit=&sender_mac=`
- Time-range queries for plotting.

4. `GET /api/stats?window=5m`
- Aggregate stats over a window.

5. `WS /ws/telemetry` (optional)
- Push latest telemetry in real time.

## Collector Service Responsibilities

1. Open serial port at 115200.
2. Parse NDJSON safely line-by-line.
3. Ignore known boot/noise lines.
4. Validate required fields and version.
5. Insert deduplicated records into DB.
6. Expose ingestion metrics (insert rate, parse errors, duplicates).

## Reliability Controls

1. Serial reconnect with exponential backoff.
2. Buffered write queue in memory with bounded size.
3. Idempotent inserts via unique key.
4. Structured error logging.
5. Startup checks for serial path and DB connectivity.
6. Alert conditions:
- no new telemetry for N seconds
- high parse error ratio
- high sequence gap ratio

## Migration Plan

Phase 1: Parallel collector

1. Keep current Web Serial dashboard for operations.
2. Run collector service in parallel to store historical data.
3. Validate database entries against receiver logs.

Phase 2: API-backed dashboard

1. Add API fetch mode to web app.
2. Keep Web Serial as fallback/debug mode.
3. Add charts and time window filters.

Phase 3: Production hardening

1. Add auth, retention policy, and backups.
2. Add dashboards for health/ingestion metrics.
3. Add deployment scripts (systemd or Docker Compose).

## Recommended First Implementation Tickets

1. Create `collector/` service skeleton with FastAPI.
2. Implement serial reader and NDJSON parser.
3. Add PostgreSQL schema and migration script.
4. Add `/api/health`, `/api/latest`, `/api/history`.
5. Add basic chart page consuming API history.
6. Add operational runbook for start/stop/restart and troubleshooting.

## Risks and Mitigations

1. Serial disconnects:
- Mitigation: auto reconnect + clear status metrics.

2. Duplicate data after reconnect:
- Mitigation: composite unique key and upsert-ignore strategy.

3. Increased latency with DB writes:
- Mitigation: small in-memory queue and batched inserts.

4. Schema drift with firmware changes:
- Mitigation: include packet version and migration process.
