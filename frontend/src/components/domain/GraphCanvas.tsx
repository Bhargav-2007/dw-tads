import { useEffect, useRef } from "react";
import cytoscape, { type Core, type StylesheetStyle } from "cytoscape";
import coseBilkent from "cytoscape-cose-bilkent";
import type { GraphNode, GraphEdge } from "../../types/api";
import { useReducedMotion } from "../../hooks/useReducedMotion";
cytoscape.use(coseBilkent);
export const nodeTypes = [
  "Actor",
  "Handle",
  "Wallet",
  "OnionService",
  "ClearnetIP",
  "PGPKey",
  "VASP",
  "Contact",
];
export function GraphCanvas({
  nodes,
  edges,
  layout = "force",
  labels = false,
  onReady,
  onSelect,
  mini = false,
}: {
  nodes: GraphNode[];
  edges: GraphEdge[];
  layout?: string;
  labels?: boolean;
  onReady?: (cy: Core) => void;
  onSelect?: (id: string, type: string) => void;
  mini?: boolean;
}) {
  const el = useRef<HTMLDivElement>(null);
  const instance = useRef<Core>();
  const reduced = useReducedMotion();
  const select = useRef(onSelect);
  select.current = onSelect;
  useEffect(() => {
    if (!el.current) return;
    const style = getComputedStyle(document.documentElement);
    const color = (key: string) => style.getPropertyValue(key).trim();
    const styles: StylesheetStyle[] = [
      {
        selector: "node",
        style: {
          label: "data(label)",
          color: color("--text-secondary"),
          "font-size": 12,
          "font-family": "Inter",
          "text-valign": "bottom",
          "text-margin-y": 8,
          "background-color": color("--status-insufficient"),
          width: 20,
          height: 20,
          "border-width": 1,
          "border-color": color("--border-strong"),
        },
      },
      {
        selector: "edge",
        style: {
          width: "mapData(confidence, 0, 1, 1, 4)",
          "line-color": color("--border-strong"),
          "curve-style": "bezier",
          "target-arrow-shape": "triangle",
          "target-arrow-color": color("--border-strong"),
          label: labels ? "data(type)" : "",
          "font-size": 12,
          color: color("--text-secondary"),
          "text-background-color": color("--surface-base"),
          "text-background-opacity": 1,
          "text-background-padding": "3px",
        },
      },
      {
        selector: ":selected",
        style: { "border-width": 3, "border-color": color("--accent-primary") },
      },
      { selector: ".dimmed", style: { opacity: 0.3 } },
    ];
    nodeTypes.forEach((type) =>
      styles.push({
        selector: `node[type = "${type}"]`,
        style: {
          "background-color":
            type === "Actor"
              ? color("--accent-primary")
              : color(`--node-${type.toLowerCase()}`),
          width:
            type === "Actor"
              ? "mapData(risk_score, 0, 1, 24, 48)"
              : type === "Wallet"
                ? "mapData(cluster_size, 1, 20, 20, 44)"
                : type === "Handle"
                  ? 20
                  : 16,
          height:
            type === "Actor"
              ? "mapData(risk_score, 0, 1, 24, 48)"
              : type === "Wallet"
                ? "mapData(cluster_size, 1, 20, 20, 44)"
                : type === "Handle"
                  ? 20
                  : 16,
        },
      }),
    );
    const ids = new Set(nodes.map((n) => n.id));
    const cy = cytoscape({
      container: el.current,
      elements: [
        ...nodes.map((n) => ({
          data: {
            ...n,
            risk_score: n.risk_score || 0,
            cluster_size: n.cluster_size || 1,
          },
        })),
        ...edges
          .filter((e) => ids.has(e.from) && ids.has(e.to))
          .map((e, i) => ({
            data: { ...e, id: `edge-${i}`, source: e.from, target: e.to },
          })),
      ],
      style: styles,
      layout: {
        name:
          layout === "force"
            ? "cose-bilkent"
            : layout === "tree"
              ? "breadthfirst"
              : "circle",
        animate: !reduced,
        animationDuration: 600,
        padding: mini ? 20 : 60,
      } as cytoscape.LayoutOptions,
      minZoom: 0.1,
      maxZoom: 4,
      wheelSensitivity: 0.25,
    });
    instance.current = cy;
    cy.on("tap", "node", (e) =>
      select.current?.(e.target.id(), e.target.data("type")),
    );
    cy.on("mouseover", "node", (e) => {
      cy.elements().addClass("dimmed");
      e.target.closedNeighborhood().removeClass("dimmed");
    });
    cy.on("mouseout", "node", () => cy.elements().removeClass("dimmed"));
    cy.on("mouseover", "edge", (e) =>
      e.target.style("label", e.target.data("type")),
    );
    cy.on("mouseout", "edge", (e) =>
      e.target.style("label", labels ? e.target.data("type") : ""),
    );
    const observer = new ResizeObserver(() => {
      cy.resize();
    });
    observer.observe(el.current);
    onReady?.(cy);
    return () => {
      observer.disconnect();
      cy.destroy();
      instance.current = undefined;
    };
  }, [nodes, edges, layout, labels, reduced, mini]);
  return (
    <div
      ref={el}
      role="img"
      aria-label={`Relationship graph with ${nodes.length} nodes and ${edges.length} edges. Use the node list for keyboard access.`}
      className={mini ? "graph-canvas mini" : "graph-canvas"}
    />
  );
}
