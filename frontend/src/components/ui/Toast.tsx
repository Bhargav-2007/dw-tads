import { useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { X, AlertCircle, CheckCircle } from "lucide-react";
import {
  useToastStore,
  type Toast as ToastData,
} from "../../stores/toastStore";
import { Button } from "./index";
import { useReducedMotion } from "../../hooks/useReducedMotion";
function Item({ toast }: { toast: ToastData }) {
  const dismiss = useToastStore((s) => s.dismiss);
  const [paused, setPaused] = useState(false);
  const [now, setNow] = useState(Date.now());
  const reduced = useReducedMotion();
  useEffect(() => {
    if (paused || (toast.retryAt && toast.retryAt > Date.now())) return;
    const id = setTimeout(() => dismiss(toast.id), 5000);
    return () => clearTimeout(id);
  }, [paused, toast, dismiss, Boolean(toast.retryAt && toast.retryAt > now)]);
  useEffect(() => {
    if (!toast.retryAt) return;
    const id = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(id);
  }, [toast.retryAt]);
  const wait = Math.max(0, Math.ceil(((toast.retryAt || 0) - now) / 1000));
  return (
    <motion.div
      className="toast"
      role={toast.kind === "error" ? "alert" : "status"}
      initial={{ opacity: 0, x: reduced ? 0 : 24 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0 }}
      onMouseEnter={() => setPaused(true)}
      onMouseLeave={() => setPaused(false)}
      onFocus={() => setPaused(true)}
      onBlur={() => setPaused(false)}
    >
      {toast.kind === "error" ? (
        <AlertCircle size={18} />
      ) : (
        <CheckCircle size={18} />
      )}
      <div>
        <p>{toast.message}</p>
        {wait > 0 && <p>Try again in {wait}s</p>}
        {toast.detail && (
          <details>
            <summary>Request details</summary>
            <code>{toast.detail}</code>
          </details>
        )}
        {toast.retry && (
          <Button
            onClick={() => {
              toast.retry?.();
              dismiss(toast.id);
            }}
          >
            Retry
          </Button>
        )}
      </div>
      <Button
        variant="ghost"
        aria-label="Dismiss notification"
        onClick={() => dismiss(toast.id)}
      >
        <X size={16} />
      </Button>
    </motion.div>
  );
}
export function Toast() {
  const toasts = useToastStore((s) => s.toasts);
  return (
    <div className="toasts">
      <AnimatePresence>
        {toasts.map((t) => (
          <Item key={t.id} toast={t} />
        ))}
      </AnimatePresence>
    </div>
  );
}
