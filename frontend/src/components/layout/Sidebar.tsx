import { NavLink } from "react-router-dom";
import {
  Activity,
  Network,
  Database,
  ShieldCheck,
  ChevronsLeft,
  ChevronsRight,
  HelpCircle,
} from "lucide-react";
import { Button } from "../ui";
import { useAuthStore } from "../../stores/authStore";
export function Sidebar({
  collapsed,
  toggle,
  onHelp,
}: {
  collapsed: boolean;
  toggle: () => void;
  onHelp: () => void;
}) {
  const admin = useAuthStore((s) => s.user?.role === "admin");
  return (
    <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>
      <div className="sidebar-label">WORKSPACE</div>
      <nav aria-label="Main navigation">
        {[
          ["/timeline", "Timeline", Activity],
          ["/graph", "Relationship graph", Network],
          ["/sources", "Data sources", Database],
          ...(admin ? [["/admin", "Administration", ShieldCheck]] : []),
        ].map(([path, label, Icon]) => {
          const Glyph = Icon as typeof Activity;
          return (
            <NavLink key={String(path)} to={String(path)} title={String(label)}>
              <Glyph size={19} />
              <span>{String(label)}</span>
            </NavLink>
          );
        })}
      </nav>
      <div className="sidebar-bottom">
        <div className="workspace-note">
          <ShieldCheck size={20} />
          <p>
            Analyst workspace<small>Evidence-led intelligence</small>
          </p>
        </div>
        <Button variant="ghost" onClick={onHelp} title="Keyboard shortcuts">
          <HelpCircle size={18} />
          <span>Keyboard shortcuts</span>
        </Button>
        <Button
          variant="ghost"
          onClick={toggle}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronsRight size={18} /> : <ChevronsLeft size={18} />}
          <span>Collapse sidebar</span>
        </Button>
      </div>
    </aside>
  );
}
