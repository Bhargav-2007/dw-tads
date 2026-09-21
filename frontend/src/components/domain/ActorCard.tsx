import type { Actor } from "../../types/api";
import { CopyButton, TierBadge } from "../common";
import { Chip } from "../ui";
export function ActorCard({
  actor,
  children,
}: {
  actor: Actor;
  children?: React.ReactNode;
}) {
  return (
    <section className="panel actor-card">
      <div className="eyebrow">ACTOR PROFILE</div>
      <div className="actor-title">
        <h1 className="mono">{actor.actor_id}</h1>
        <CopyButton value={actor.actor_id} />
        <TierBadge tier={actor.tier} />
      </div>
      <div className="chips">
        {(Array.isArray(actor.category)
          ? actor.category
          : [actor.category]
        ).map((c) => (
          <Chip key={c}>{c}</Chip>
        ))}
      </div>
      <div className="actor-risk">
        <strong>{actor.risk_score.toFixed(2)}</strong>
        <span className="muted">Risk score / 1.00</span>
      </div>
      {children}
    </section>
  );
}
