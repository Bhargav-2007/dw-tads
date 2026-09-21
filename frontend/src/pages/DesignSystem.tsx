import { Button, Chip, Kbd } from "../components/ui";
import { TierBadge, ConfidenceBar } from "../components/common";
import { tiers } from "../lib/tier";
export default function DesignSystem() {
  return (
    <div className="page">
      <div className="eyebrow">DW-TADS / DESIGN SYSTEM</div>
      <h1>Quiet by default.</h1>
      <p className="muted">A focused, evidence-led analyst workspace.</p>
      <div className="stats-grid">
        {["base", "panel", "elevated", "hover", "active"].map((s) => (
          <div
            key={s}
            className="panel swatch"
            style={{ background: `var(--surface-${s})` }}
          >
            {s}
          </div>
        ))}
      </div>
      <section className="panel tab-content">
        <h2>Semantic states</h2>
        <div className="chips">
          {tiers.map((t) => (
            <TierBadge key={t} tier={t} />
          ))}
        </div>
        <h2>Controls</h2>
        <div className="toolbar-actions">
          <Button variant="primary">Primary action</Button>
          <Button>Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Chip active>Selected</Chip>
          <Kbd>⌘ K</Kbd>
        </div>
        <h2>Evidence confidence</h2>
        <ConfidenceBar value={0.86} />
        <h2>Technical typography</h2>
        <p className="mono">a8b2:7f90:ce34 · 2026-09-21T08:30:00Z</p>
      </section>
    </div>
  );
}
