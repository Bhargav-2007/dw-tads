CREATE TABLE IF NOT EXISTS intel_sources (
 name TEXT PRIMARY KEY, url TEXT NOT NULL, last_attempt TIMESTAMPTZ,
 last_success TIMESTAMPTZ, error TEXT, last_sha TEXT
);
CREATE TABLE IF NOT EXISTS intel_snapshots (
 sha256 TEXT PRIMARY KEY, source TEXT NOT NULL REFERENCES intel_sources(name),
 object_key TEXT NOT NULL, captured_at TIMESTAMPTZ NOT NULL, byte_count BIGINT NOT NULL,
 processed_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS intel_records (
 id TEXT PRIMARY KEY, source TEXT NOT NULL, external_id TEXT NOT NULL,
 kind TEXT NOT NULL CHECK(kind IN ('vulnerability','malware','technique')),
 title TEXT NOT NULL, description TEXT NOT NULL, published_at TIMESTAMPTZ NOT NULL,
 first_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(), last_seen TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 source_url TEXT NOT NULL, snapshot_sha TEXT NOT NULL REFERENCES intel_snapshots(sha256),
 data JSONB NOT NULL, active BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS intel_records_timeline ON intel_records(published_at DESC,id);
CREATE INDEX IF NOT EXISTS intel_records_source ON intel_records(source,kind);
CREATE TABLE IF NOT EXISTS intel_relationships (
 source_id TEXT REFERENCES intel_records(id), target_id TEXT REFERENCES intel_records(id),
 type TEXT NOT NULL CHECK(type='uses'), snapshot_sha TEXT NOT NULL REFERENCES intel_snapshots(sha256),
 PRIMARY KEY(source_id,target_id,type)
);
