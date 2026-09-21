import { useApi } from "../../hooks/useApi";
import type { SourcesResponse } from "../../types/api";
import { Search, Command, Menu, LogOut, Shield } from "lucide-react";
import { Link } from "react-router-dom";
import { Avatar, Button, Kbd, Popover } from "../ui";
import { useAuthStore } from "../../stores/authStore";
import { useFocusStore } from "../../stores/focusStore";
export function TopBar({
  onSearch,
  onMenu,
}: {
  onSearch: () => void;
  onMenu: () => void;
}) {
  const { user, logout } = useAuthStore();
  const { data: sources } = useApi<SourcesResponse>("/query/sources");
  const failures = sources?.sources?.filter((s) => !s.success).length || 0;
  const focus = useFocusStore((s) => s.focusMode);
  return (
    <header className="topbar">
      <Button
        variant="ghost"
        className="mobile-menu"
        aria-label="Toggle navigation"
        onClick={onMenu}
      >
        <Menu size={20} />
      </Button>
      <Link className="brand" to="/timeline">
        <Shield size={25} />
        <span>DW-TADS</span>
        <small>INTELLIGENCE</small>
      </Link>
      <button className="search-trigger" onClick={onSearch}>
        <Search size={16} />
        <span>Search actors, handles, wallets…</span>
        <Kbd>/</Kbd>
      </button>
      <div className="top-actions">
        {focus && <span className="eyebrow">FOCUS</span>}
        <Link to="/sources" className="muted sources-link">
          {failures > 0 && <span className="dot status-error" />}Sources
          {failures > 0 && <span>({failures} failed)</span>}
        </Link>
        <Button
          variant="ghost"
          aria-label="Open command palette"
          onClick={onSearch}
        >
          <Command size={17} />
          <Kbd>K</Kbd>
        </Button>
        <Popover label={user?.username || "Analyst"}>
          <div className="user-info">
            <Avatar name={user?.username || "A"} />
            <span>{user?.role}</span>
          </div>
          <Button onClick={logout}>
            <LogOut size={16} />
            Sign out
          </Button>
        </Popover>
      </div>
    </header>
  );
}
