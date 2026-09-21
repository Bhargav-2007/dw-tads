import { useState } from "react";
import { useParams, Link } from "react-router-dom";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import { useApi } from "../hooks/useApi";
import { useReducedMotion } from "../hooks/useReducedMotion";
import type {
  ActorResponse,
  AuditResponse,
  GraphResponse,
  RecordData,
} from "../types/api";
import { Button, Tabs } from "../components/ui";
import {
  EmptyState,
  Skeleton,
  ConfidenceBar,
  CopyButton,
  RelativeTime,
} from "../components/common";
import { ActorCard } from "../components/domain/ActorCard";
import { IdentifierTable } from "../components/domain/IdentifierTable";
import { EvidenceTimeline } from "../components/domain/EvidenceTimeline";
import { AuditTable } from "../components/domain/AuditTable";
import { GraphCanvas } from "../components/domain/GraphCanvas";
import { useTimelineStore } from "../stores/timelineStore";
import { exportQuery } from "../lib/api";
import { textValue } from "../lib/format";
const tabs = [
  "Overview",
  "Identifiers",
  "Infrastructure",
  "Personas",
  "Blockchain",
  "Evidence",
  "Audit",
];
export default function Actor() {
  const { actor_id = "" } = useParams();
  const { data, loading, error, refresh } = useApi<ActorResponse>(
    `/query/actor/${encodeURIComponent(actor_id)}`,
  );
  const { data: graph } = useApi<GraphResponse>(
    `/query/graph?actor_id=${encodeURIComponent(actor_id)}&depth=1`,
  );
  const [tab, setTab] = useState("Overview");
  const { data: audit } = useApi<AuditResponse>(
    tab === "Audit" ? "/query/audit?limit=100" : null,
  );
  const queryId = useTimelineStore((s) =>
    s.results.some((a) => a.actor_id === actor_id) ? s.queryId : null,
  );
  const reduced = useReducedMotion();
  const [exporting, setExporting] = useState(false);
  if (loading)
    return (
      <div className="page">
        <Skeleton rows={10} />
      </div>
    );
  if (error || !data?.actor)
    return (
      <EmptyState
        error
        title="Actor unavailable"
        description={error || "The response did not include an actor."}
        action={<Button onClick={refresh}>Try again</Button>}
      />
    );
  const confidence =
    typeof data.attribution_confidence === "number"
      ? data.attribution_confidence
      : Number(
          data.attribution_confidence?.score ?? data.actor.confidence ?? 0,
        );
  const contributions =
    typeof data.attribution_confidence === "object"
      ? data.attribution_confidence.contributions || data.attribution_confidence
      : data.actor.source_confidence || {};
  const contributionRows =
    typeof contributions === "object" && contributions
      ? Object.entries(contributions)
          .filter(([, v]) => typeof v === "number")
          .map(([name, value]) => ({ name, value }))
      : [];
  const profile = data.behavioral_profile || {};
  const rawHistogram =
    profile.hourly_activity ||
    profile.hour_histogram ||
    profile.hourly_histogram;
  const histogram = Array.isArray(rawHistogram)
    ? rawHistogram.map((v, i) =>
        typeof v === "number"
          ? { hour: String(i).padStart(2, "0"), count: v }
          : (v as RecordData),
      )
    : [];
  return (
    <div className="page">
      <div className="breadcrumb">
        <Link to="/timeline">Investigation Timeline</Link>
        <span>/</span>
        <span className="mono">{actor_id}</span>
      </div>
      <div className="actor-grid">
        <div>
          <ActorCard actor={data.actor}>
            <div className="toolbar-actions">
              <Button
                variant="primary"
                disabled={!queryId}
                loading={exporting}
                title="Exports the originating timeline query"
                onClick={async () => {
                  if (queryId) {
                    setExporting(true);
                    try {
                      await exportQuery(queryId, "pdf");
                    } catch {
                    } finally {
                      setExporting(false);
                    }
                  }
                }}
              >
                Export query PDF
              </Button>
              <Button disabled title="Case API is not specified">
                Add to case
              </Button>
              <Button disabled title="Comparison API is not specified">
                Compare
              </Button>
            </div>
          </ActorCard>
          <section className="panel actor-content">
            <Tabs tabs={tabs} value={tab} onChange={setTab} />
            <div
              className="tab-content"
              role="tabpanel"
              aria-label={tab}
              key={tab}
            >
              {tab === "Overview" && (
                <>
                  <h3>Attribution contributions</h3>
                  {contributionRows.length ? (
                    <ResponsiveContainer width="100%" height={220}>
                      <BarChart data={contributionRows} layout="vertical">
                        <XAxis
                          type="number"
                          domain={[0, 1]}
                          stroke="var(--text-secondary)"
                        />
                        <YAxis
                          type="category"
                          dataKey="name"
                          width={120}
                          stroke="var(--text-secondary)"
                        />
                        <Tooltip
                          contentStyle={{
                            background: "var(--surface-panel)",
                            borderColor: "var(--border-default)",
                          }}
                        />
                        <Bar
                          dataKey="value"
                          fill="var(--accent-primary)"
                          isAnimationActive={!reduced}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="muted">No contribution breakdown reported.</p>
                  )}
                  <h3>Behavioral profile</h3>
                  <p className="muted">
                    Time zone:{" "}
                    {textValue(profile.timezone || profile.time_zone)}
                  </p>
                  {histogram.length ? (
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={histogram}>
                        <XAxis dataKey="hour" stroke="var(--text-secondary)" />
                        <YAxis stroke="var(--text-secondary)" />
                        <Tooltip
                          contentStyle={{
                            background: "var(--surface-panel)",
                            borderColor: "var(--border-default)",
                          }}
                        />
                        <Bar
                          dataKey="count"
                          fill="var(--accent-primary)"
                          isAnimationActive={!reduced}
                        />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <p className="muted">No hourly activity reported.</p>
                  )}
                  {profile.anomaly_score != null && (
                    <>
                      <h3>Anomaly score</h3>
                      <ConfidenceBar value={Number(profile.anomaly_score)} />
                    </>
                  )}
                  <h3>Recent activity</h3>
                  <EvidenceTimeline
                    entries={(data.evidence_chain || []).slice(0, 10)}
                  />
                </>
              )}
              {tab === "Identifiers" && (
                <>
                  <IdentifierTable
                    title="Handles"
                    rows={data.handles || []}
                    columns={[
                      "handle_id",
                      "platform",
                      "first_seen",
                      "confidence",
                    ]}
                  />
                  <IdentifierTable
                    title="PGP keys"
                    rows={data.pgp_keys || []}
                    columns={["fingerprint", "algorithm", "first_seen"]}
                  />
                  <IdentifierTable
                    title="Wallets"
                    rows={data.wallets || []}
                    columns={[
                      "address",
                      "currency",
                      "first_seen",
                      "confidence",
                    ]}
                  />
                  <IdentifierTable
                    title="Contacts"
                    rows={data.contacts || []}
                    columns={["type", "value", "first_seen"]}
                  />
                </>
              )}
              {tab === "Infrastructure" && (
                <>
                  <IdentifierTable
                    title="Onion services"
                    rows={data.onion_services || []}
                    columns={["onion_address", "type", "last_seen"]}
                  />
                  <IdentifierTable
                    title="Clearnet IPs"
                    rows={data.clearnet_ips || []}
                    columns={["ip_address", "hosting_provider", "confidence"]}
                  />
                  <IdentifierTable
                    title="Correlations"
                    rows={data.correlations || []}
                  />
                </>
              )}
              {tab === "Personas" &&
                ((data.stylometric_matches || []).length ? (
                  (data.stylometric_matches || []).map((m, i) => (
                    <div className="persona-card" key={i}>
                      <h3>{textValue(m.other_handle)}</h3>
                      <p>Similarity</p>
                      <ConfidenceBar value={Number(m.similarity_score || 0)} />
                      <p>Confidence</p>
                      <ConfidenceBar value={Number(m.confidence || 0)} />
                      {m.signals && typeof m.signals === "object"
                        ? Object.entries(m.signals).map(([k, v]) => (
                            <div key={k}>
                              {k}
                              <ConfidenceBar value={Number(v)} />
                            </div>
                          ))
                        : null}
                      {m.actor_id != null && (
                        <Link
                          to={`/actor/${encodeURIComponent(String(m.actor_id))}`}
                        >
                          Open related actor →
                        </Link>
                      )}
                    </div>
                  ))
                ) : (
                  <EmptyState
                    title="No stylometric matches"
                    description="No persona correlations were reported."
                  />
                ))}
              {tab === "Blockchain" && (
                <>
                  {(data.wallet_clusters || []).map((c, i) => (
                    <details className="persona-card" key={i}>
                      <summary>
                        Wallet cluster {textValue(c.cluster_id || i + 1)}
                      </summary>
                      <pre>{JSON.stringify(c, null, 2)}</pre>
                    </details>
                  ))}
                  <IdentifierTable
                    title="VASP deposits"
                    rows={data.vasp_deposits || []}
                    columns={[
                      "wallet",
                      "vasp_name",
                      "country",
                      "kyc_traceable",
                    ]}
                  />
                  {!data.wallet_clusters?.length && (
                    <p className="muted">No wallet clusters reported.</p>
                  )}
                </>
              )}
              {tab === "Evidence" && (
                <>
                  <h3>Merkle root</h3>
                  <p className="mono break-word">
                    {data.merkle_root || "Not reported"}
                    {data.merkle_root && (
                      <CopyButton value={data.merkle_root} />
                    )}
                  </p>
                  <EvidenceTimeline entries={data.evidence_chain || []} />
                </>
              )}
              {tab === "Audit" && (
                <>
                  <p className="muted">
                    Actor matches within the latest 100 audit entries.
                  </p>
                  <AuditTable
                    rows={(audit?.results || [])
                      .filter(
                        (r) =>
                          r.resource === actor_id ||
                          r.resource === `/actor/${actor_id}`,
                      )
                      .slice(0, 10)}
                  />
                </>
              )}
            </div>
          </section>
        </div>
        <aside className="actor-aside">
          <section className="panel confidence-panel">
            <div className="section-label">ATTRIBUTION CONFIDENCE</div>
            <div className="gauge">
              <svg
                viewBox="0 0 160 160"
                aria-label={`Confidence ${Math.round(confidence * 100)} percent`}
                role="img"
              >
                <circle
                  cx="80"
                  cy="80"
                  r="65"
                  fill="none"
                  stroke="var(--surface-active)"
                  strokeWidth="7"
                />
                <circle
                  className="gauge-fill"
                  cx="80"
                  cy="80"
                  r="65"
                  fill="none"
                  stroke="var(--accent-primary)"
                  strokeWidth="7"
                  strokeDasharray={`${Math.max(0, Math.min(1, confidence)) * 408.4} 408.4`}
                  transform="rotate(-90 80 80)"
                />
              </svg>
              <strong>
                {Math.round(confidence * 100)}
                <small>%</small>
              </strong>
            </div>
            <p className="muted">Supported by available evidence</p>
          </section>
          <section className="panel mini-graph">
            <h3>Connected entities</h3>
            {graph?.nodes?.length ? (
              <GraphCanvas nodes={graph.nodes} edges={graph.edges} mini />
            ) : (
              <p className="muted">No relationships available</p>
            )}
            <Link to={`/graph?actor_id=${encodeURIComponent(actor_id)}`}>
              Open full graph →
            </Link>
          </section>
          <section className="panel quick-stats">
            <h3>Quick stats</h3>
            <dl>
              <div>
                <dt>Handles</dt>
                <dd>{data.handles?.length || 0}</dd>
              </div>
              <div>
                <dt>Wallets</dt>
                <dd>{data.wallets?.length || 0}</dd>
              </div>
              <div>
                <dt>First seen</dt>
                <dd>
                  <RelativeTime value={data.actor.first_seen || ""} />
                </dd>
              </div>
              <div>
                <dt>Last seen</dt>
                <dd>
                  <RelativeTime value={data.actor.last_seen} />
                </dd>
              </div>
            </dl>
          </section>
          <section className="panel quick-stats">
            <h3>Related actors</h3>
            {data.related_actors?.length ? (
              data.related_actors.slice(0, 5).map((a, i) => (
                <p key={i}>
                  <Link to={`/actor/${encodeURIComponent(String(a.actor_id))}`}>
                    {textValue(a.actor_id)}
                  </Link>
                </p>
              ))
            ) : (
              <p className="muted">No related actors reported.</p>
            )}
          </section>
        </aside>
      </div>
    </div>
  );
}
