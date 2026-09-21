-- DW-TADS PostgreSQL schema — evidence-first, append-only audit trail
-- Reference: Section 5 of architecture specification

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─── Users ───────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS users (
    user_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username     TEXT UNIQUE NOT NULL,
    role         TEXT NOT NULL CHECK (role IN ('analyst','senior_analyst','admin','auditor')),
    password_hash TEXT NOT NULL,
    mfa_secret   TEXT NOT NULL,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    last_login   TIMESTAMPTZ
);

-- ─── Evidence ────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS evidence (
    evidence_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sha256       CHAR(64) UNIQUE NOT NULL,
    source_url   TEXT,
    source_type  TEXT NOT NULL,
    captured_at  TIMESTAMPTZ NOT NULL,
    minio_bucket TEXT NOT NULL,
    minio_key    TEXT NOT NULL,
    merkle_root  CHAR(64),
    ingested_by  TEXT NOT NULL
);

-- ─── Audit log (append-only, advisory-lock-protected hash chain) ─────────────

CREATE TABLE IF NOT EXISTS audit_log (
    audit_id    BIGSERIAL PRIMARY KEY,
    event_type  TEXT NOT NULL,
    actor_user  TEXT NOT NULL,
    action      TEXT NOT NULL,
    resource    TEXT,
    query_hash  CHAR(64),
    result_hash CHAR(64),
    prev_hash   CHAR(64),
    this_hash   CHAR(64) NOT NULL,
    ts          TIMESTAMPTZ DEFAULT NOW(),
    metadata    JSONB DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(ts DESC);

CREATE OR REPLACE FUNCTION audit_log_immutable() RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'audit_log is append-only';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS audit_log_no_update ON audit_log;
CREATE TRIGGER audit_log_no_update BEFORE UPDATE OR DELETE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION audit_log_immutable();

-- ─── Source fetch observability (every external call logged here) ─────────────

CREATE TABLE IF NOT EXISTS source_fetches (
    fetch_id     BIGSERIAL PRIMARY KEY,
    source_name  TEXT NOT NULL,
    url          TEXT NOT NULL,
    fetched_at   TIMESTAMPTZ DEFAULT NOW(),
    record_count INT NOT NULL DEFAULT 0,
    http_status  INT,
    duration_ms  INT,
    cache_hit    BOOLEAN NOT NULL DEFAULT FALSE,
    success      BOOLEAN NOT NULL DEFAULT TRUE,
    error        TEXT
);
CREATE INDEX IF NOT EXISTS idx_fetches_source ON source_fetches(source_name, fetched_at DESC);

-- ─── Wallet clusters (blockchain-clusterer output) ────────────────────────────

CREATE TABLE IF NOT EXISTS wallet_clusters (
    cluster_id  TEXT PRIMARY KEY,
    currency    TEXT NOT NULL,
    addresses   TEXT[] NOT NULL,
    heuristic   TEXT NOT NULL,
    updated_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ─── Behavioral profiles (behavioral-profiler output) ────────────────────────

CREATE TABLE IF NOT EXISTS behavior_profile (
    profile_id                BIGSERIAL PRIMARY KEY,
    handle_id                 TEXT NOT NULL,
    post_count                INT NOT NULL,
    estimated_timezone_offset INT NOT NULL,
    hour_histogram            JSONB NOT NULL,
    mean_word_count           REAL NOT NULL,
    std_word_count            REAL NOT NULL,
    frequency_variance        REAL NOT NULL,
    anomaly_score             REAL NOT NULL,
    is_anomaly                BOOLEAN NOT NULL,
    computed_at               TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_bp_handle_time ON behavior_profile(handle_id, computed_at DESC);

-- ─── Idempotency table (message deduplication) ───────────────────────────────

CREATE TABLE IF NOT EXISTS processed (
    consumer  TEXT NOT NULL,
    event_id  TEXT NOT NULL,
    PRIMARY KEY (consumer, event_id)
);

-- ─── Outbox (transactional outbox for Kafka publish) ─────────────────────────

CREATE TABLE IF NOT EXISTS outbox (
    id       BIGSERIAL PRIMARY KEY,
    event_id TEXT UNIQUE NOT NULL,
    topic    TEXT NOT NULL,
    payload  JSONB NOT NULL,
    sent     BOOLEAN NOT NULL DEFAULT FALSE
);

-- ─── Seed demo users (Argon2id hash of 'demo_password') ──────────────────────

INSERT INTO users (username, role, password_hash, mfa_secret) VALUES
    ('analyst1',  'analyst',        '$argon2id$v=19$m=65536,t=3,p=4$MGSx2k3t058aH1fCc4em7w$fUIdYPAXxAO6xKDS4REvZJFP1L8JhJgFwxkGABMG6FI', 'JBSWY3DPEHPK3PXP'),
    ('senior1',   'senior_analyst', '$argon2id$v=19$m=65536,t=3,p=4$MGSx2k3t058aH1fCc4em7w$fUIdYPAXxAO6xKDS4REvZJFP1L8JhJgFwxkGABMG6FI', 'KRSXGZDFNQQGK3DF'),
    ('admin1',    'admin',          '$argon2id$v=19$m=65536,t=3,p=4$MGSx2k3t058aH1fCc4em7w$fUIdYPAXxAO6xKDS4REvZJFP1L8JhJgFwxkGABMG6FI', 'MFRGGZDFMZTWQ2LK'),
    ('judge1',    'auditor',        '$argon2id$v=19$m=65536,t=3,p=4$MGSx2k3t058aH1fCc4em7w$fUIdYPAXxAO6xKDS4REvZJFP1L8JhJgFwxkGABMG6FI', 'GEZDGNBVGY3TQOJQ')
ON CONFLICT (username) DO NOTHING;
