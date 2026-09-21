ALTER TABLE intel_snapshots ADD COLUMN IF NOT EXISTS object_version TEXT;
ALTER TABLE intel_records ADD COLUMN IF NOT EXISTS classification TEXT NOT NULL DEFAULT 'U' CHECK (classification='U');
ALTER TABLE intel_records ADD COLUMN IF NOT EXISTS source_confidence TEXT CHECK (source_confidence IN ('A','B','C','D','E','F'));
ALTER TABLE intel_records ADD COLUMN IF NOT EXISTS information_confidence SMALLINT CHECK (information_confidence BETWEEN 1 AND 6);
CREATE TABLE intel_record_versions (
 id TEXT NOT NULL, snapshot_sha TEXT NOT NULL REFERENCES intel_snapshots(sha256),
 source TEXT NOT NULL REFERENCES intel_sources(name), payload JSONB NOT NULL,
 leaf_hash CHAR(64) NOT NULL, recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
 PRIMARY KEY(id,snapshot_sha)
);
CREATE INDEX intel_record_versions_snapshot ON intel_record_versions(snapshot_sha);
CREATE TABLE intel_relationship_versions (
 source_id TEXT NOT NULL,target_id TEXT NOT NULL,type TEXT NOT NULL CHECK(type='uses'),
 snapshot_sha TEXT NOT NULL REFERENCES intel_snapshots(sha256),
 PRIMARY KEY(source_id,target_id,type,snapshot_sha),
 FOREIGN KEY(source_id,snapshot_sha) REFERENCES intel_record_versions(id,snapshot_sha),
 FOREIGN KEY(target_id,snapshot_sha) REFERENCES intel_record_versions(id,snapshot_sha)
);
CREATE TABLE intel_merkle_anchors (
 snapshot_sha TEXT PRIMARY KEY REFERENCES intel_snapshots(sha256),
 root CHAR(64) NOT NULL, leaf_count INTEGER NOT NULL CHECK(leaf_count>0),
 scheme TEXT NOT NULL DEFAULT 'sha256-domain-separated-duplicate-odd-v1',
 recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE FUNCTION intel_history_immutable() RETURNS TRIGGER AS $$
BEGIN RAISE EXCEPTION 'intelligence evidence history is append-only'; END;
$$ LANGUAGE plpgsql;
CREATE TRIGGER intel_versions_no_update BEFORE UPDATE OR DELETE ON intel_record_versions
 FOR EACH ROW EXECUTE FUNCTION intel_history_immutable();
CREATE TRIGGER intel_relationship_versions_no_update BEFORE UPDATE OR DELETE ON intel_relationship_versions
 FOR EACH ROW EXECUTE FUNCTION intel_history_immutable();
CREATE TRIGGER intel_anchors_no_update BEFORE UPDATE OR DELETE ON intel_merkle_anchors
 FOR EACH ROW EXECUTE FUNCTION intel_history_immutable();
CREATE VIEW intel_history_records AS
 SELECT v.id,v.source,v.payload->>'external_id' AS external_id,v.payload->>'kind' AS kind,
 v.payload->>'title' AS title,v.payload->>'description' AS description,
 (v.payload->>'published_at')::timestamptz AS published_at,
 s.captured_at AS first_seen,s.captured_at AS last_seen,
 v.payload->>'source_url' AS source_url,v.snapshot_sha,v.payload->'data' AS data,TRUE AS active,
 'U'::text AS classification,NULL::text AS source_confidence,NULL::smallint AS information_confidence,
 s.captured_at AS valid_from,
 (SELECT min(s2.captured_at) FROM intel_snapshots s2
  WHERE s2.source=s.source AND s2.captured_at>s.captured_at AND s2.processed_at IS NOT NULL) AS valid_until,
 v.recorded_at
 FROM intel_record_versions v JOIN intel_snapshots s ON s.sha256=v.snapshot_sha;
