import { lazy, Suspense, useEffect } from "react";
import { useTimelineStore } from "./stores/timelineStore";
import { useGraphStore } from "./stores/graphStore";
import { Navigate, Outlet, Route, Routes } from "react-router-dom";
import { useAuthStore } from "./stores/authStore";
import { useToastStore } from "./stores/toastStore";
import { useFocusStore } from "./stores/focusStore";
import { AppShell } from "./components/layout/AppShell";
import { Toast } from "./components/ui/Toast";
import { Skeleton } from "./components/common";
const Login = lazy(() => import("./pages/Login"));
const Timeline = lazy(() => import("./pages/Timeline"));
const Actor = lazy(() => import("./pages/Actor"));
const Graph = lazy(() => import("./pages/Graph"));
const Sources = lazy(() => import("./pages/Sources"));
const Admin = lazy(() => import("./pages/Admin"));
const NotFound = lazy(() => import("./pages/NotFound"));
const DesignSystem = lazy(() => import("./pages/DesignSystem"));
function Protected() {
  return useAuthStore((s) => s.token) ? (
    <Outlet />
  ) : (
    <Navigate to="/login" replace />
  );
}
function AdminOnly() {
  const admin = useAuthStore((s) => s.user?.role === "admin");
  useEffect(() => {
    if (!admin)
      useToastStore
        .getState()
        .push({ kind: "error", message: "Insufficient permissions" });
  }, [admin]);
  return admin ? <Admin /> : <Navigate to="/timeline" replace />;
}
export default function App() {
  const logout = useAuthStore((s) => s.logout);
  const token = useAuthStore((s) => s.token);
  useEffect(() => {
    if (!token) {
      useTimelineStore.setState({
        results: [],
        queryId: null,
        resultHash: "",
        error: null,
      });
      useGraphStore.setState({
        actorId: "",
        nodes: [],
        edges: [],
        error: null,
      });
    }
  }, [token]);
  useEffect(() => {
    window.addEventListener("dwtds:unauthorized", logout);
    return () => window.removeEventListener("dwtds:unauthorized", logout);
  }, [logout]);
  useEffect(() => {
    if (!token) return;
    const remaining =
      Number(sessionStorage.getItem("dwtds_expires")) - Date.now();
    const timer = setTimeout(logout, Math.max(0, remaining));
    return () => clearTimeout(timer);
  }, [token, logout]);
  useEffect(() => {
    let context: AudioContext | undefined;
    const click = (e: KeyboardEvent) => {
      if (
        !useFocusStore.getState().sound ||
        !["Enter", "Escape"].includes(e.key)
      )
        return;
      context ??= new AudioContext();
      const oscillator = context.createOscillator(),
        gain = context.createGain();
      gain.gain.setValueAtTime(0.1, context.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, context.currentTime + 0.02);
      oscillator.frequency.value = 800;
      oscillator.connect(gain);
      gain.connect(context.destination);
      oscillator.start();
      oscillator.stop(context.currentTime + 0.02);
    };
    window.addEventListener("keydown", click);
    return () => {
      window.removeEventListener("keydown", click);
      void context?.close();
    };
  }, []);
  return (
    <>
      <div className="desktop-required">
        <h1>DW-TADS</h1>
        <p>DW-TADS is designed for desktop use. Please use a wider viewport.</p>
      </div>
      <div className="desktop-app">
        <Suspense
          fallback={
            <div className="page">
              <Skeleton rows={8} />
            </div>
          }
        >
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/design-system" element={<DesignSystem />} />
            <Route element={<Protected />}>
              <Route element={<AppShell />}>
                <Route index element={<Navigate to="/timeline" replace />} />
                <Route path="/timeline" element={<Timeline />} />
                <Route path="/actor/:actor_id" element={<Actor />} />
                <Route path="/graph" element={<Graph />} />
                <Route path="/sources" element={<Sources />} />
                <Route path="/admin" element={<AdminOnly />} />
                <Route path="*" element={<NotFound />} />
              </Route>
            </Route>
          </Routes>
        </Suspense>
      </div>
      <Toast />
    </>
  );
}
