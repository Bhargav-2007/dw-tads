import { CheckCircle, XCircle, ExternalLink } from "lucide-react";
import type { Source } from "../../types/api";
import { RelativeTime } from "../common";
import { CountUp, Badge } from "../ui";
import { safeUrl } from "../../lib/format";
export function SourcesTable({ sources }: { sources: Source[] }) {
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            {[
              "Source",
              "Last fetch",
              "Records",
              "HTTP status",
              "Cache",
              "Result",
              "Error",
            ].map((t) => (
              <th key={t}>{t}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sources.map((s, i) => (
            <tr key={`${s.name}-${i}`}>
              <td>
                <a href={safeUrl(s.url)} target="_blank" rel="noreferrer">
                  {s.name} <ExternalLink size={12} />
                </a>
                <small className="source-url mono">{s.url}</small>
              </td>
              <td>
                <RelativeTime value={s.last_fetch} />
              </td>
              <td className="mono">
                <CountUp value={s.record_count} />
              </td>
              <td>
                <Badge kind={s.http_status < 400 ? "success" : "error"}>
                  {s.http_status}
                </Badge>
              </td>
              <td>
                {typeof s.cache_hit === "string"
                  ? s.cache_hit
                  : s.cache_hit
                    ? "Hit"
                    : "Miss"}
              </td>
              <td>
                {s.success ? (
                  <span className="status-good">
                    <CheckCircle size={15} />
                    Success
                  </span>
                ) : (
                  <span className="status-error">
                    <XCircle size={15} />
                    Failed
                  </span>
                )}
              </td>
              <td>
                {s.error ? (
                  <details>
                    <summary>{s.error.slice(0, 35)}</summary>
                    <p>{s.error}</p>
                  </details>
                ) : (
                  "—"
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
