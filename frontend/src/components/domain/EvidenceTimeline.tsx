import type { RecordData } from "../../types/api";
import { safeUrl, textValue, shortHash } from "../../lib/format";
import { CopyButton, RelativeTime, EmptyState } from "../common";
export function EvidenceTimeline({ entries }: { entries: RecordData[] }) {
  return !entries.length ? (
    <EmptyState
      title="No evidence reported"
      description="Evidence will appear here when supplied by the query."
    />
  ) : (
    <ol className="evidence-timeline">
      {entries.map((e, i) => (
        <li key={i}>
          <div className="timeline-point" />
          <div>
            <h3>{textValue(e.event_type || e.type || "Evidence captured")}</h3>
            {e.captured_at != null && (
              <RelativeTime value={String(e.captured_at)} />
            )}
            <p className="mono">
              {shortHash(textValue(e.sha256), 16)}
              {e.sha256 != null && <CopyButton value={String(e.sha256)} />}
            </p>
            {e.source_url != null && (
              <a
                href={safeUrl(String(e.source_url))}
                target="_blank"
                rel="noreferrer"
              >
                {String(e.source_url)}
              </a>
            )}
            <p className="mono muted">{textValue(e.minio_key)}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
