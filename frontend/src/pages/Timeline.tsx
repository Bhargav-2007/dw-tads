import { useEffect, useMemo, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import {
  RefreshCw,
  Download,
  SlidersHorizontal,
  ArrowDown,
  Activity,
  Users,
  ShieldCheck,
  Database,
} from "lucide-react";
import { useTimelineStore, defaultFilters } from "../stores/timelineStore";
import { useApi } from "../hooks/useApi";
import type { SourcesResponse, Actor, Tier } from "../types/api";
import {
  Button,
  Chip,
  Select,
  Input,
  Checkbox,
  Popover,
  CountUp,
  ProgressBar,
} from "../components/ui";
import {
  ConfidenceBar,
  TierBadge,
  EmptyState,
  Skeleton,
  RelativeTime,
  CorrelationIdBadge,
} from "../components/common";
import { exportQuery } from "../lib/api";
const categories = [
  "drugs",
  "arms",
  "hacking",
  "stolen_data",
  "terror",
  "fraud",
];
export default function Timeline() {
  const { results, loading, error, filters, queryId, setFilters, fetch } =
    useTimelineStore();
  const { data: sources } = useApi<SourcesResponse>("/query/sources");
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [compact, setCompact] = useState(false);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [hidden, setHidden] = useState<string[]>([]);
  const [sort, setSort] = useState<{
    key: "risk_score" | "confidence" | "actor_id";
    desc: boolean;
  }>({ key: "risk_score", desc: true });
  const [scroll, setScroll] = useState(0);
  const [exporting, setExporting] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    void fetch();
    window.addEventListener("dwtds:retry", fetch);
    return () => window.removeEventListener("dwtds:retry", fetch);
  }, [
    fetch,
    filters.start,
    filters.end,
    filters.minConfidence,
    filters.category,
  ]);
  const rows = useMemo(
    () =>
      results
        .filter(
          (a) =>
            (filters.tier === "All" || a.tier === filters.tier) &&
            a.confidence <= filters.maxConfidence &&
            `${a.actor_id} ${JSON.stringify(a.handles)}`
              .toLowerCase()
              .includes(search.toLowerCase()),
        )
        .sort((a, b) => {
          const av = a[sort.key],
            bv = b[sort.key];
          return (
            (typeof av === "number" && typeof bv === "number"
              ? av - bv
              : String(av).localeCompare(String(bv))) * (sort.desc ? -1 : 1)
          );
        }),
    [results, filters, search, sort],
  );
  useEffect(() => {
    setScroll(0);
    if (scrollRef.current) scrollRef.current.scrollTop = 0;
    setSelected(new Set());
  }, [rows]);
  useEffect(() => {
    const timer = setInterval(() => {
      if (!document.hidden && !useTimelineStore.getState().loading)
        void fetch();
    }, 60000);
    return () => clearInterval(timer);
  }, [fetch]);
  const height = compact ? 48 : 64;
  const virtual = rows.length > 100;
  const start = virtual ? Math.max(0, Math.floor(scroll / height) - 5) : 0;
  const end = virtual ? Math.min(rows.length, start + 25) : rows.length;
  const active = results.filter(
    (a) => Date.parse(a.last_seen) >= Date.now() - 7 * 86400000,
  ).length;
  const changeSort = (key: typeof sort.key) =>
    setSort((s) => ({ key, desc: s.key === key ? !s.desc : true }));
  const columns = [
    ["actor_id", "Actor ID"],
    ["risk_score", "Risk"],
    ["tier", "Tier"],
    ["category", "Categories"],
    ["handles", "Handles"],
    ["wallets", "Wallets"],
    ["confidence", "Confidence"],
    ["last_seen", "Last seen"],
  ];
  const visible = columns.filter(([k]) => !hidden.includes(k));
  const preset = (days: string) => {
    if (!days) return;
    setFilters({
      start: new Date(Date.now() - Number(days) * 86400000)
        .toISOString()
        .slice(0, 10),
      end: new Date().toISOString().slice(0, 10),
    });
  };
  const cell = (a: Actor, k: string) => {
    switch (k) {
      case "actor_id":
        return <span className="actor-link mono">{a.actor_id}</span>;
      case "risk_score":
        return <span className="mono">{a.risk_score.toFixed(2)}</span>;
      case "tier":
        return <TierBadge tier={a.tier} />;
      case "category": {
        const cats = Array.isArray(a.category) ? a.category : [a.category];
        return (
          <div className="chips">
            {cats.slice(0, 3).map((c) => (
              <Chip key={c}>{c.replace("_", " ")}</Chip>
            ))}
            {cats.length > 3 && <span>+{cats.length - 3}</span>}
          </div>
        );
      }
      case "handles":
        return (
          <span className="mono truncate" title={JSON.stringify(a.handles)}>
            {(a.handles || [])
              .slice(0, 3)
              .map((h) =>
                typeof h === "string"
                  ? h
                  : String(h.handle_id || h.handle || ""),
              )
              .join(", ") || "—"}
          </span>
        );
      case "wallets":
        return <span className="mono">{a.wallets?.length || 0}</span>;
      case "confidence":
        return <ConfidenceBar value={a.confidence} />;
      case "last_seen":
        return <RelativeTime value={a.last_seen} />;
    }
  };
  return (
    <div className="page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">INTELLIGENCE / OVERVIEW</div>
          <h1>Investigation Timeline</h1>
          <p>Track actors, evaluate signals, and follow the evidence.</p>
        </div>
        <Button onClick={() => void fetch()} loading={loading}>
          <RefreshCw size={16} />
          Refresh
        </Button>
      </div>
      <div className="stats-grid">
        {[
          [Users, "Total actors", results.length, "In current query"],
          [
            ShieldCheck,
            "High confidence",
            results.filter((a) => a.tier === "HIGH").length,
            "Attribution tier: HIGH",
          ],
          [Activity, "Active this week", active, "Seen in the last 7 days"],
          [
            Database,
            "Sources online",
            sources?.sources.filter((s) => s.success).length,
            sources
              ? `of ${sources.distinct_sources} reporting sources`
              : "Awaiting source status",
          ],
        ].map(([Icon, label, value, note]) => {
          const Glyph = Icon as typeof Users;
          return (
            <div className="stat-card" key={String(label)}>
              <div>
                <span>{String(label)}</span>
                <Glyph size={17} />
              </div>
              <strong>
                {loading ? (
                  "—"
                ) : typeof value === "number" ? (
                  <CountUp value={value} />
                ) : (
                  "—"
                )}
              </strong>
              <small>{String(note)}</small>
            </div>
          );
        })}
      </div>
      <section className="panel filters">
        <div className="section-label">
          <SlidersHorizontal size={15} />
          QUERY FILTERS
        </div>
        <div className="filter-row">
          <Select
            label="Time range"
            onChange={(e) => preset(e.target.value)}
            defaultValue=""
          >
            <option value="">Custom / all time</option>
            <option value="1">Last 24 hours</option>
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </Select>
          <Input
            label="Start date"
            type="date"
            value={filters.start}
            max={filters.end || undefined}
            onChange={(e) => setFilters({ start: e.target.value })}
          />
          <Input
            label="End date"
            type="date"
            min={filters.start || undefined}
            value={filters.end}
            onChange={(e) => setFilters({ end: e.target.value })}
          />
          <div className="range-group">
            <label>
              Confidence {filters.minConfidence.toFixed(2)}–
              {filters.maxConfidence.toFixed(2)}
            </label>
            <div>
              <input
                aria-label="Minimum confidence"
                type="range"
                min="0"
                max="1"
                step=".05"
                value={filters.minConfidence}
                onChange={(e) =>
                  setFilters({
                    minConfidence: Math.min(
                      +e.target.value,
                      filters.maxConfidence,
                    ),
                  })
                }
              />
              <input
                aria-label="Maximum confidence"
                type="range"
                min="0"
                max="1"
                step=".05"
                value={filters.maxConfidence}
                onChange={(e) =>
                  setFilters({
                    maxConfidence: Math.max(
                      +e.target.value,
                      filters.minConfidence,
                    ),
                  })
                }
              />
            </div>
          </div>
        </div>
        <div className="filter-bottom">
          <div className="chips">
            <span className="muted">Category</span>
            {categories.map((c) => (
              <Chip
                key={c}
                active={filters.category.includes(c)}
                onClick={() =>
                  setFilters({
                    category: filters.category.includes(c)
                      ? filters.category.filter((x) => x !== c)
                      : [...filters.category, c],
                  })
                }
              >
                {c.replace("_", " ")}
              </Chip>
            ))}
          </div>
          <div className="segments" aria-label="Tier filter">
            {["All", "HIGH", "MEDIUM", "LOW"].map((t) => (
              <button
                key={t}
                aria-pressed={filters.tier === t}
                onClick={() => setFilters({ tier: t as Tier | "All" })}
              >
                {t}
              </button>
            ))}
          </div>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setFilters({ ...defaultFilters });
              setSearch("");
            }}
          >
            Clear
          </Button>
        </div>
      </section>
      <section className="panel results">
        {loading && results.length > 0 && <ProgressBar />}
        <div className="table-toolbar">
          <div>
            <h2>
              Actor intelligence <span className="count">{rows.length}</span>
            </h2>
            <small className="muted">
              Showing {rows.length} of {results.length}
              {selected.size ? ` · ${selected.size} selected` : ""}
            </small>
          </div>
          <div className="toolbar-actions">
            <input
              aria-label="Filter loaded actors"
              placeholder="Filter actors…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <Popover label="Columns">
              {columns.map(([k, l]) => (
                <label className="check-label" key={k}>
                  <Checkbox
                    checked={!hidden.includes(k)}
                    disabled={k === "actor_id"}
                    onChange={() =>
                      setHidden((h) =>
                        h.includes(k) ? h.filter((x) => x !== k) : [...h, k],
                      )
                    }
                  />
                  {l}
                </label>
              ))}
            </Popover>
            <Button size="sm" onClick={() => setCompact((c) => !c)}>
              {compact ? "Compact" : "Comfortable"}
            </Button>
            <Popover label="Export">
              {(["csv", "json", "pdf"] as const).map((f) => (
                <Button
                  key={f}
                  disabled={!queryId || exporting || loading}
                  onClick={async () => {
                    if (!queryId) return;
                    setExporting(true);
                    try {
                      await exportQuery(queryId, f);
                    } catch {
                    } finally {
                      setExporting(false);
                    }
                  }}
                >
                  <Download size={15} />
                  {f.toUpperCase()}
                </Button>
              ))}
              <small>
                Exports the server query. Local tier, search, selection and
                maximum-confidence filters are not applied.
              </small>
            </Popover>
          </div>
        </div>
        {error ? (
          <EmptyState
            error
            title="Timeline unavailable"
            description={error}
            action={<Button onClick={() => void fetch()}>Try again</Button>}
          />
        ) : loading && !results.length ? (
          <Skeleton rows={7} />
        ) : !rows.length ? (
          <EmptyState
            title="No actors in this view"
            description="Adjust the query filters or wait for ingested intelligence to become available."
          />
        ) : (
          <div
            ref={scrollRef}
            className="table-scroll"
            style={{ maxHeight: 560 }}
            onScroll={(e) => setScroll(e.currentTarget.scrollTop)}
          >
            <table className={compact ? "compact" : ""}>
              <thead>
                <tr>
                  <th>
                    <Checkbox
                      aria-label="Select all visible actors"
                      checked={
                        rows.length > 0 &&
                        rows.every((a) => selected.has(a.actor_id))
                      }
                      onChange={(e) =>
                        setSelected(
                          e.target.checked
                            ? new Set(rows.map((a) => a.actor_id))
                            : new Set(),
                        )
                      }
                    />
                  </th>
                  {visible.map(([k, l]) => (
                    <th
                      key={k}
                      aria-sort={
                        sort.key === k
                          ? sort.desc
                            ? "descending"
                            : "ascending"
                          : undefined
                      }
                    >
                      {["actor_id", "risk_score", "confidence"].includes(k) ? (
                        <button
                          onClick={() => changeSort(k as typeof sort.key)}
                        >
                          {l}
                          {sort.key === k && (
                            <ArrowDown
                              size={13}
                              style={{
                                transform: sort.desc
                                  ? "none"
                                  : "rotate(180deg)",
                              }}
                            />
                          )}
                        </button>
                      ) : (
                        l
                      )}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {virtual && start > 0 && (
                  <tr aria-hidden="true">
                    <td
                      colSpan={visible.length + 1}
                      style={{ height: start * height, padding: 0 }}
                    />
                  </tr>
                )}
                {rows.slice(start, end).map((a, i) => (
                  <tr
                    key={a.actor_id}
                    tabIndex={0}
                    aria-label={`Open actor ${a.actor_id}`}
                    className={selected.has(a.actor_id) ? "selected-row" : ""}
                    style={{
                      height,
                      animation: i < 30 ? "row-enter 200ms both" : undefined,
                      animationDelay: i < 30 ? `${i * 20}ms` : undefined,
                    }}
                    onClick={() =>
                      navigate(`/actor/${encodeURIComponent(a.actor_id)}`)
                    }
                    onKeyDown={(e) => {
                      if (e.target !== e.currentTarget) return;
                      if (e.key === "Enter")
                        navigate(`/actor/${encodeURIComponent(a.actor_id)}`);
                      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
                        e.preventDefault();
                        const next =
                          e.key === "ArrowDown"
                            ? e.currentTarget.nextElementSibling
                            : e.currentTarget.previousElementSibling;
                        (next as HTMLElement)?.focus();
                      }
                    }}
                  >
                    <td onClick={(e) => e.stopPropagation()}>
                      <Checkbox
                        aria-label={`Select ${a.actor_id}`}
                        checked={selected.has(a.actor_id)}
                        onChange={() =>
                          setSelected((s) => {
                            const n = new Set(s);
                            n.has(a.actor_id)
                              ? n.delete(a.actor_id)
                              : n.add(a.actor_id);
                            return n;
                          })
                        }
                      />
                    </td>
                    {visible.map(([k]) => (
                      <td key={k}>{cell(a, k)}</td>
                    ))}
                  </tr>
                ))}
                {virtual && end < rows.length && (
                  <tr aria-hidden="true">
                    <td
                      colSpan={visible.length + 1}
                      style={{
                        height: (rows.length - end) * height,
                        padding: 0,
                      }}
                    />
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
        <div className="table-footer">
          <span>Confidence reflects evidence strength, not certainty.</span>
          <CorrelationIdBadge />
        </div>
      </section>
    </div>
  );
}
