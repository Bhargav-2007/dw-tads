import { useState } from "react";
import { Check, Copy, Inbox, AlertCircle } from "lucide-react";
import { Button } from "../ui";
import { tierColor, getTier } from "../../lib/tier";
import { useRelativeTime } from "../../hooks/useRelativeTime";
import { useToastStore } from "../../stores/toastStore";
import { correlationId } from "../../lib/api";
import type { Tier } from "../../types/api";
export function TierBadge({ tier }: { tier: Tier }) {
  return (
    <span className="badge" style={{ color: tierColor(tier) }}>
      <span className="dot" />
      {tier}
    </span>
  );
}
export function ConfidenceBar({ value }: { value: number }) {
  const safe = Math.max(0, Math.min(1, value || 0));
  return (
    <div className="confidence" title={String(value)}>
      <span className="track">
        <span
          style={{
            width: `${safe * 100}%`,
            background: tierColor(getTier(safe)),
          }}
        />
      </span>
      <span className="mono">{safe.toFixed(2)}</span>
    </div>
  );
}
export function CopyButton({ value }: { value: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <Button
      size="sm"
      variant="ghost"
      aria-label="Copy value"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(value);
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        } catch {
          useToastStore
            .getState()
            .push({ kind: "error", message: "Clipboard access unavailable" });
        }
      }}
    >
      {copied ? <Check size={14} /> : <Copy size={14} />}
    </Button>
  );
}
export function CorrelationIdBadge() {
  return correlationId ? (
    <span className="mono muted" title={correlationId}>
      Request {correlationId.slice(0, 8)}
      <CopyButton value={correlationId} />
    </span>
  ) : null;
}
export function EmptyState({
  title,
  description,
  action,
  error = false,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
  error?: boolean;
}) {
  const Icon = error ? AlertCircle : Inbox;
  return (
    <div className="empty">
      <Icon size={40} />
      <h2>{title}</h2>
      <p>{description}</p>
      {action}
    </div>
  );
}
export function Skeleton({ rows = 6 }: { rows?: number }) {
  return (
    <div aria-label="Loading data" aria-busy="true">
      {Array.from({ length: rows }, (_, i) => (
        <div key={i} className="skeleton" />
      ))}
    </div>
  );
}
export function RelativeTime({ value }: { value: string }) {
  const formatted = useRelativeTime(value);
  return (
    <time title={value} dateTime={value} className="mono">
      {formatted}
    </time>
  );
}
