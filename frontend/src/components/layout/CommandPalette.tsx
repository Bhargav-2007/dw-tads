import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, ArrowUpRight } from "lucide-react";
import { Modal } from "../ui";
import { useTimelineStore } from "../../stores/timelineStore";
import { useAuthStore } from "../../stores/authStore";
export function CommandPalette({ onClose }: { onClose: () => void }) {
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState(0);
  const navigate = useNavigate();
  const actors = useTimelineStore((s) => s.results);
  const admin = useAuthStore((s) => s.user?.role === "admin");
  const options = [
    { group: "Actions", label: "Investigation Timeline", path: "/timeline" },
    { group: "Actions", label: "Relationship Graph", path: "/graph" },
    { group: "Sources", label: "Data Sources", path: "/sources" },
    ...(admin
      ? [{ group: "Actions", label: "Administration", path: "/admin" }]
      : []),
    ...actors.flatMap((a) => [
      {
        group: "Actors",
        label: a.actor_id,
        path: `/actor/${encodeURIComponent(a.actor_id)}`,
      },
      ...(a.handles || []).map((h) => ({
        group: "Handles",
        label:
          typeof h === "string" ? h : String(h.handle_id || h.handle || ""),
        path: `/actor/${encodeURIComponent(a.actor_id)}`,
      })),
      ...(a.wallets || []).map((w) => ({
        group: "Wallets",
        label: typeof w === "string" ? w : String(w.address || ""),
        path: `/actor/${encodeURIComponent(a.actor_id)}`,
      })),
    ]),
  ]
    .filter((x) => x.label.toLowerCase().includes(query.toLowerCase()))
    .slice(0, 30);
  const go = (path: string) => {
    onClose();
    navigate(path);
  };
  return (
    <Modal title="Search or jump to" onClose={onClose}>
      <div className="palette-search">
        <Search size={20} />
        <input
          aria-label="Search or jump to"
          role="combobox"
          aria-expanded="true"
          aria-controls="command-results"
          aria-activedescendant={
            options[selected] ? `command-${selected}` : undefined
          }
          value={query}
          placeholder="Actors, handles, wallets, or pages…"
          onChange={(e) => {
            setQuery(e.target.value);
            setSelected(0);
          }}
          onKeyDown={(e) => {
            if (e.key === "ArrowDown" || e.key === "ArrowUp") {
              e.preventDefault();
              setSelected(
                (s) =>
                  (s + (e.key === "ArrowDown" ? 1 : -1) + options.length) %
                  Math.max(1, options.length),
              );
            }
            if (e.key === "Enter" && options[selected])
              go(options[selected].path);
          }}
        />
      </div>
      <div id="command-results" role="listbox" className="command-results">
        {options.map((x, i) => (
          <button
            id={`command-${i}`}
            role="option"
            aria-selected={selected === i}
            className={selected === i ? "active" : ""}
            key={`${x.group}-${i}`}
            onClick={() => go(x.path)}
          >
            <span>
              <small>{x.group}</small>
              {x.label}
            </span>
            <ArrowUpRight size={16} />
          </button>
        ))}
        {!options.length && (
          <p className="muted">
            No matches in the loaded results. Load a timeline query to search
            actors.
          </p>
        )}
      </div>
    </Modal>
  );
}
