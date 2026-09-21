import type { RecordData } from "../../types/api";
import { textValue, shortHash } from "../../lib/format";
import { CopyButton, ConfidenceBar, EmptyState } from "../common";
export function IdentifierTable({
  title,
  rows,
  columns,
}: {
  title: string;
  rows: RecordData[];
  columns?: string[];
}) {
  const keys =
    columns || Array.from(new Set(rows.flatMap(Object.keys))).slice(0, 6);
  return (
    <section className="data-section">
      <h3>{title}</h3>
      {!rows.length ? (
        <EmptyState
          title="No records reported"
          description={`The API has not supplied ${title.toLowerCase()} for this actor.`}
        />
      ) : (
        <div className="table-scroll">
          <table>
            <thead>
              <tr>
                {keys.map((k) => (
                  <th key={k}>{k.replaceAll("_", " ")}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={i}>
                  {keys.map((k) => (
                    <td key={k}>
                      {k === "confidence" ? (
                        <ConfidenceBar value={Number(r[k])} />
                      ) : (
                        <span className="mono" title={textValue(r[k])}>
                          {shortHash(textValue(r[k]), 14)}
                          {["fingerprint", "address", "sha256"].includes(k) &&
                            r[k] != null && <CopyButton value={String(r[k])} />}
                        </span>
                      )}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
