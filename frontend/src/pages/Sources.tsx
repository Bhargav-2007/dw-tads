import { RefreshCw } from "lucide-react";
import { useApi } from "../hooks/useApi";
import type { SourcesResponse } from "../types/api";
import { Button, CountUp } from "../components/ui";
import { EmptyState, Skeleton, RelativeTime } from "../components/common";
import { SourcesTable } from "../components/domain/SourcesTable";
export default function Sources() {
  const { data, loading, error, refresh } =
    useApi<SourcesResponse>("/query/sources");
  const sources = data?.sources || [];
  const latest = sources
    .map((s) => s.last_fetch)
    .filter(Boolean)
    .sort()
    .at(-1);
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">INTELLIGENCE / COLLECTION</div>
          <h1>Data Sources</h1>
          <p>Live fetches and cache state</p>
        </div>
        <Button onClick={refresh} loading={loading}>
          <RefreshCw size={16} />
          Refresh
        </Button>
      </div>
      <div className="stats-grid">
        <div className="stat-card">
          <span>Total sources</span>
          <strong>
            {data ? <CountUp value={data.distinct_sources} /> : "—"}
          </strong>
          <small>Distinct reporting sources</small>
        </div>
        <div className="stat-card">
          <span>Records ingested</span>
          <strong>{data ? <CountUp value={data.total_records} /> : "—"}</strong>
          <small>Returned by the collection service</small>
        </div>
        <div className="stat-card">
          <span>Last fetch</span>
          <strong className="small-stat">
            {latest ? <RelativeTime value={latest} /> : "—"}
          </strong>
          <small>Most recent source update</small>
        </div>
        <div className="stat-card">
          <span>Cache hit ratio</span>
          <strong>
            {sources.length
              ? `${Math.round((sources.filter((s) => s.cache_hit === true || s.cache_hit === "hit").length / sources.length) * 100)}%`
              : "—"}
          </strong>
          <small>Reported snapshot; 24h history unavailable</small>
        </div>
      </div>
      <section className="panel">
        <div className="table-toolbar">
          <h2>Source health</h2>
          <span className="muted">
            {sources.filter((s) => !s.success).length} failed sources
          </span>
        </div>
        {loading ? (
          <Skeleton />
        ) : error ? (
          <EmptyState
            error
            title="Sources unavailable"
            description={error}
            action={<Button onClick={refresh}>Try again</Button>}
          />
        ) : !sources.length ? (
          <EmptyState
            title="No sources have been fetched yet"
            description="Run scripts/load-live-data.sh on a connected host."
          />
        ) : (
          <SourcesTable sources={sources} />
        )}
      </section>
    </div>
  );
}
