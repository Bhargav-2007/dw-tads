import { useState } from "react";
import { CheckCircle, AlertTriangle, RefreshCw } from "lucide-react";
import { useApi } from "../hooks/useApi";
import type { AuditResponse } from "../types/api";
import { Tabs, Button, Input } from "../components/ui";
import { EmptyState, Skeleton } from "../components/common";
import { AuditTable } from "../components/domain/AuditTable";
function System() {
  const health = useApi<{ status: string }>("/health");
  const ready = useApi<{ status: string }>("/ready");
  const metrics = useApi<string>("/metrics");
  return (
    <div className="system-grid">
      <section className="panel">
        <h3>Analyst API</h3>
        <p>
          Health:{" "}
          {health.loading
            ? "Checking…"
            : health.error || health.data?.status || "Unknown"}
        </p>
        <p>
          Readiness:{" "}
          {ready.loading
            ? "Checking…"
            : ready.error || ready.data?.status || "Unknown"}
        </p>
        <Button
          onClick={() => {
            health.refresh();
            ready.refresh();
            metrics.refresh();
          }}
        >
          Refresh health
        </Button>
      </section>
      <section className="panel">
        <h3>Service metrics</h3>
        {metrics.error ? (
          <p>{metrics.error}</p>
        ) : (
          <pre>{metrics.data || "Awaiting metrics…"}</pre>
        )}
        <p className="muted">
          Kafka lag, cache size and service versions are shown only when exposed
          by the metrics endpoint. Per-container health endpoints are not
          specified.
        </p>
      </section>
    </div>
  );
}
export default function Admin() {
  const [tab, setTab] = useState("Audit");
  const [event, setEvent] = useState("");
  const [user, setUser] = useState("");
  const [since, setSince] = useState("");
  const [end, setEnd] = useState("");
  const { data, loading, error, refresh } = useApi<AuditResponse>(
    tab === "Audit"
      ? `/query/audit?limit=500${since ? `&since=${encodeURIComponent(new Date(since).toISOString())}` : ""}`
      : null,
  );
  const rows = (data?.results || []).filter(
    (r) =>
      (!event || r.event_type.toLowerCase().includes(event.toLowerCase())) &&
      (!user || r.actor_user.toLowerCase().includes(user.toLowerCase())) &&
      (!end || Date.parse(r.ts) < Date.parse(end) + 86400000),
  );
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">WORKSPACE / ADMINISTRATION</div>
          <h1>Administration</h1>
          <p>Access oversight, audit integrity, and service health.</p>
        </div>
        <Button onClick={refresh}>
          <RefreshCw size={16} />
          Refresh
        </Button>
      </div>
      <section className="panel">
        <Tabs
          tabs={["Users", "Audit", "System"]}
          value={tab}
          onChange={setTab}
        />
        <div className="tab-content">
          {tab === "Users" && (
            <EmptyState
              title="User management is not connected"
              description="The supplied API contract does not expose user listing, MFA reset, role changes, or account disabling. These operations require backend endpoints and server-side authorization."
            />
          )}
          {tab === "System" && <System />}
          {tab === "Audit" && (
            <>
              {data && (
                <div
                  className={`chain-status ${data.chain_valid ? "status-good" : "status-error"}`}
                >
                  {data.chain_valid ? (
                    <CheckCircle size={20} />
                  ) : (
                    <AlertTriangle size={20} />
                  )}
                  <strong>
                    {data.chain_valid
                      ? `Chain verified over ${data.results.length} returned entries`
                      : `Audit chain broken at ${data.broken_at || "unknown entry"}`}
                  </strong>
                </div>
              )}
              <div className="filter-row">
                <Input
                  label="Event type"
                  value={event}
                  onChange={(e) => setEvent(e.target.value)}
                />
                <Input
                  label="Actor user"
                  value={user}
                  onChange={(e) => setUser(e.target.value)}
                />
                <Input
                  label="Since"
                  type="date"
                  value={since}
                  onChange={(e) => setSince(e.target.value)}
                />
                <Input
                  label="Until"
                  type="date"
                  value={end}
                  onChange={(e) => setEnd(e.target.value)}
                />
              </div>
              {loading ? (
                <Skeleton />
              ) : error ? (
                <EmptyState
                  error
                  title="Audit unavailable"
                  description={error}
                />
              ) : (
                <AuditTable rows={rows} />
              )}
            </>
          )}
        </div>
      </section>
    </div>
  );
}
