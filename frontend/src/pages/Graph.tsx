import { useEffect, useRef, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import type { Core } from "cytoscape";
import { ZoomIn, ZoomOut, Maximize, RotateCcw, Download } from "lucide-react";
import { useGraphStore } from "../stores/graphStore";
import { GraphCanvas, nodeTypes } from "../components/domain/GraphCanvas";
import {
  Button,
  Input,
  Select,
  Chip,
  Popover,
  Checkbox,
} from "../components/ui";
import { EmptyState, Skeleton } from "../components/common";
import { downloadBlob } from "../lib/api";
const xml = (s: string) =>
  s.replace(
    /[<>&"']/g,
    (c) =>
      ({
        "<": "&lt;",
        ">": "&gt;",
        "&": "&amp;",
        '"': "&quot;",
        "'": "&apos;",
      })[c]!,
  );
export default function Graph() {
  const store = useGraphStore();
  const [params] = useSearchParams();
  const [actor, setActor] = useState(params.get("actor_id") || store.actorId);
  const [layout, setLayout] = useState("force");
  const [labels, setLabels] = useState(false);
  const [selected, setSelected] = useState<{ id: string; type: string } | null>(
    null,
  );
  const cy = useRef<Core>();
  useEffect(() => {
    const id = params.get("actor_id");
    if (id) {
      store.configure({ actorId: id });
      void store.fetch();
    }
  }, [params]);
  const nodes = store.nodes.filter(
    (n) =>
      (!store.filters.nodeTypes.length ||
        store.filters.nodeTypes.includes(n.type)) &&
      (store.filters.tier === "All" || n.tier === store.filters.tier),
  );
  const ids = new Set(nodes.map((n) => n.id));
  const edges = store.edges.filter((e) => ids.has(e.from) && ids.has(e.to));
  function graphML() {
    const value = `<?xml version="1.0" encoding="UTF-8"?><graphml xmlns="http://graphml.graphdrawing.org/xmlns"><key id="label" for="node" attr.name="label" attr.type="string"/><key id="type" for="all" attr.name="type" attr.type="string"/><key id="confidence" for="edge" attr.name="confidence" attr.type="double"/><graph edgedefault="directed">${nodes.map((n) => `<node id="${xml(n.id)}"><data key="label">${xml(n.label)}</data><data key="type">${xml(n.type)}</data></node>`).join("")}${edges.map((e, i) => `<edge id="e${i}" source="${xml(e.from)}" target="${xml(e.to)}"><data key="type">${xml(e.type)}</data><data key="confidence">${e.confidence}</data></edge>`).join("")}</graph></graphml>`;
    downloadBlob(
      new Blob([value], { type: "application/xml" }),
      "dw-tads.graphml",
    );
  }
  return (
    <div className="graph-page">
      <div className="page-heading">
        <div>
          <div className="eyebrow">INTELLIGENCE / CONNECTIONS</div>
          <h1>Relationship Graph</h1>
          <p>Explore the links behind an attribution.</p>
        </div>
        <span className="mono muted">
          {nodes.length} nodes · {edges.length} edges
        </span>
      </div>
      <div className="graph-workspace">
        {store.loading ? (
          <Skeleton rows={10} />
        ) : store.error ? (
          <EmptyState
            error
            title="Graph unavailable"
            description={store.error}
          />
        ) : nodes.length ? (
          <GraphCanvas
            nodes={nodes}
            edges={edges}
            layout={layout}
            labels={labels}
            onReady={(c) => {
              cy.current = c;
            }}
            onSelect={(id, type) => setSelected({ id, type })}
          />
        ) : (
          <EmptyState
            title="Follow a connection"
            description="Enter an actor ID and load its relationship graph."
          />
        )}
        <form
          className="graph-controls glass"
          onSubmit={(e) => {
            e.preventDefault();
            store.configure({ actorId: actor });
            void store.fetch();
          }}
        >
          <div className="section-label">GRAPH EXPLORER</div>
          <Input
            label="Actor ID"
            className="mono"
            value={actor}
            required
            onChange={(e) => setActor(e.target.value)}
            placeholder="Enter actor ID"
          />
          <div className="filter-row">
            <Select
              label="Depth"
              value={store.depth}
              onChange={(e) => store.configure({ depth: +e.target.value })}
            >
              {[1, 2, 3].map((d) => (
                <option key={d}>{d}</option>
              ))}
            </Select>
            <Select
              label="Layout"
              value={layout}
              onChange={(e) => setLayout(e.target.value)}
            >
              <option value="force">Force</option>
              <option value="tree">Tree</option>
              <option value="circle">Circle</option>
            </Select>
          </div>
          <Button variant="primary" type="submit" loading={store.loading}>
            Load graph
          </Button>
          <hr />
          <span className="muted text-xs">NODE TYPES · ALL BY DEFAULT</span>
          <div className="chips">
            {nodeTypes.map((t) => (
              <Chip
                key={t}
                active={store.filters.nodeTypes.includes(t)}
                onClick={() =>
                  store.configure({
                    filters: {
                      ...store.filters,
                      nodeTypes: store.filters.nodeTypes.includes(t)
                        ? store.filters.nodeTypes.filter((x) => x !== t)
                        : [...store.filters.nodeTypes, t],
                    },
                  })
                }
              >
                {t}
              </Chip>
            ))}
          </div>
          <Select
            label="Attribution tier"
            value={store.filters.tier}
            onChange={(e) =>
              store.configure({
                filters: { ...store.filters, tier: e.target.value },
              })
            }
          >
            {["All", "HIGH", "MEDIUM", "LOW", "INSUFFICIENT"].map((t) => (
              <option key={t}>{t}</option>
            ))}
          </Select>
          <label className="check-label">
            <Checkbox
              checked={labels}
              onChange={(e) => setLabels(e.target.checked)}
            />
            Show edge labels
          </label>
        </form>
        <div className="graph-actions glass">
          <Button
            aria-label="Zoom in"
            onClick={() => cy.current?.zoom(cy.current.zoom() * 1.2)}
          >
            <ZoomIn size={17} />
          </Button>
          <Button
            aria-label="Zoom out"
            onClick={() => cy.current?.zoom(cy.current.zoom() / 1.2)}
          >
            <ZoomOut size={17} />
          </Button>
          <Button
            aria-label="Fit graph"
            onClick={() => cy.current?.fit(undefined, 60)}
          >
            <Maximize size={17} />
          </Button>
          <Button
            aria-label="Reset graph"
            onClick={() => {
              setLayout("force");
              store.configure({ filters: { nodeTypes: [], tier: "All" } });
              cy.current?.fit();
            }}
          >
            <RotateCcw size={17} />
          </Button>
          <Popover label="Export">
            <Button
              disabled={!nodes.length}
              onClick={() => {
                if (cy.current)
                  downloadBlob(
                    cy.current.png({
                      output: "blob",
                      full: true,
                      bg: getComputedStyle(document.documentElement)
                        .getPropertyValue("--surface-base")
                        .trim(),
                    }),
                    "dw-tads-graph.png",
                  );
              }}
            >
              <Download size={14} />
              PNG
            </Button>
            <Button disabled={!nodes.length} onClick={graphML}>
              GraphML
            </Button>
          </Popover>
        </div>
        <div className="graph-legend glass">
          <div className="section-label">ENTITY LEGEND</div>
          {nodeTypes.map((t) => (
            <span key={t}>
              <i style={{ background: `var(--node-${t.toLowerCase()})` }} />
              {t}
            </span>
          ))}
          <small>Edge width indicates confidence.</small>
        </div>
        {selected && (
          <div className="graph-selection glass">
            <strong>{selected.type}</strong>
            <code>{selected.id}</code>
            {selected.type === "Actor" && (
              <Link to={`/actor/${encodeURIComponent(selected.id)}`}>
                Open actor profile →
              </Link>
            )}
          </div>
        )}
      </div>
      <details className="panel node-list">
        <summary>Accessible node list ({nodes.length})</summary>
        {nodes.map((n) => (
          <button
            key={n.id}
            onClick={() => {
              setSelected({ id: n.id, type: n.type });
              cy.current?.getElementById(n.id).select();
            }}
          >
            {n.type} · {n.label}
          </button>
        ))}
      </details>
    </div>
  );
}
