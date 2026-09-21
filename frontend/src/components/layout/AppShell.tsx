import { useCallback, useEffect, useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import { TopBar } from "./TopBar";
import { Sidebar } from "./Sidebar";
import { CommandPalette } from "./CommandPalette";
import { Modal, Kbd, Checkbox } from "../ui";
import { useKeyboard } from "../../hooks/useKeyboard";
import { useFocusStore } from "../../stores/focusStore";
import { shortcuts, isEditing } from "../../lib/shortcuts";
import { useReducedMotion } from "../../hooks/useReducedMotion";
export function AppShell() {
  const [collapsed, setCollapsed] = useState(false);
  const [drawer, setDrawer] = useState(false);
  const [palette, setPalette] = useState(false);
  const [help, setHelp] = useState(false);
  const { focusMode, zenMode, toggle, setZen, sound, setSound } =
    useFocusStore();
  const reduced = useReducedMotion();
  const location = useLocation();
  useKeyboard(
    useCallback(
      (e: KeyboardEvent) => {
        if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
          e.preventDefault();
          setHelp(false);
          setPalette((v) => !v);
          return;
        }
        if (isEditing(e.target)) return;
        if (e.key === "/") {
          e.preventDefault();
          setHelp(false);
          setPalette(true);
        }
        if (e.key.toLowerCase() === "f") toggle();
        if (e.key === "Escape") {
          setDrawer(false);
          if (focusMode) toggle();
        }
        if (e.key === "?") {
          setPalette(false);
          setHelp(true);
        }
      },
      [focusMode, toggle],
    ),
  );
  useEffect(() => {
    let timer: ReturnType<typeof setTimeout>;
    const active = () => {
      setZen(false);
      clearTimeout(timer);
      timer = setTimeout(() => setZen(true), 30000);
    };
    active();
    const events = ["mousemove", "keydown", "scroll", "pointerdown"];
    events.forEach((x) => window.addEventListener(x, active, true));
    return () => {
      clearTimeout(timer);
      events.forEach((x) => window.removeEventListener(x, active, true));
    };
  }, [setZen]);
  useEffect(() => setDrawer(false), [location.pathname]);
  return (
    <div
      className={`app-shell ${collapsed ? "is-collapsed" : ""} ${focusMode ? "focus-mode" : ""} ${zenMode ? "zen-mode" : ""} ${drawer ? "drawer-open" : ""}`}
    >
      <a href="#main" className="skip-link">
        Skip to content
      </a>
      <TopBar
        onSearch={() => setPalette(true)}
        onMenu={() => setDrawer((v) => !v)}
      />
      <Sidebar
        collapsed={collapsed}
        toggle={() => setCollapsed((v) => !v)}
        onHelp={() => setHelp(true)}
      />
      <motion.main
        id="main"
        key={location.pathname}
        initial={{ opacity: 0, y: reduced ? 0 : 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: reduced ? 0.1 : 0.2 }}
      >
        <Outlet />
      </motion.main>
      {palette && <CommandPalette onClose={() => setPalette(false)} />}
      {help && (
        <Modal
          title="Keyboard shortcuts & preferences"
          onClose={() => setHelp(false)}
        >
          <dl className="shortcut-list">
            {shortcuts.map(([key, description]) => (
              <div key={key}>
                <dt>
                  <Kbd>{key}</Kbd>
                </dt>
                <dd>{description}</dd>
              </div>
            ))}
          </dl>
          <label className="check-label">
            <Checkbox
              checked={sound}
              onChange={(e) => setSound(e.target.checked)}
            />
            Enable quiet keyboard click sound
          </label>
          <p className="muted">
            Sound is off by default. Motion follows your system preference.
          </p>
        </Modal>
      )}
    </div>
  );
}
