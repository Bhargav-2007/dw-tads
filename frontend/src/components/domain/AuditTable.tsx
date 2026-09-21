import { useState } from "react";
import { Fragment } from "react";
import type { AuditEntry } from "../../types/api";
import { RelativeTime, CopyButton, EmptyState } from "../common";
import { shortHash } from "../../lib/format";
export function AuditTable({ rows }: { rows: AuditEntry[] }) {
  const [open, setOpen] = useState<string | null>(null);
  if (!rows.length)
    return (
      <EmptyState
        title="No audit entries"
        description="No entries match this view."
      />
    );
  return (
    <div className="table-scroll">
      <table>
        <thead>
          <tr>
            {[
              "Audit ID",
              "Timestamp",
              "Event",
              "User",
              "Action",
              "Resource",
              "Query hash",
            ].map((k) => (
              <th key={k}>{k}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <Fragment key={r.audit_id || i}>
              <tr>
                <td>
                  <button
                    className="text-link mono"
                    aria-expanded={open === r.audit_id}
                    onClick={() =>
                      setOpen(open === r.audit_id ? null : r.audit_id)
                    }
                  >
                    {r.audit_id}
                  </button>
                </td>
                <td>
                  <RelativeTime value={r.ts} />
                </td>
                <td>{r.event_type}</td>
                <td>{r.actor_user}</td>
                <td>{r.action}</td>
                <td className="mono">{r.resource}</td>
                <td className="mono">{shortHash(r.query_hash || "—", 6)}</td>
              </tr>
              {open === r.audit_id && (
                <tr>
                  <td colSpan={7}>
                    <div className="audit-detail">
                      <p>
                        Query hash:{" "}
                        <code>{r.query_hash || "Not reported"}</code>
                        <CopyButton value={r.query_hash || ""} />
                      </p>
                      <p>
                        Result hash:{" "}
                        <code>{r.result_hash || "Not reported"}</code>
                        <CopyButton value={r.result_hash || ""} />
                      </p>
                      <pre>{JSON.stringify(r.metadata || r, null, 2)}</pre>
                    </div>
                  </td>
                </tr>
              )}
            </Fragment>
          ))}
        </tbody>
      </table>
    </div>
  );
}
