import {
  Component,
  useEffect,
  useRef,
  useState,
  type ReactNode,
  type ButtonHTMLAttributes,
  type InputHTMLAttributes,
  type SelectHTMLAttributes,
} from "react";
import { createPortal } from "react-dom";
import { motion } from "framer-motion";
import { X, LoaderCircle, AlertTriangle } from "lucide-react";
import clsx from "clsx";
import { scaleIn } from "../../lib/motion";
import { useReducedMotion } from "../../hooks/useReducedMotion";
export function Button({
  variant = "secondary",
  size = "md",
  loading,
  children,
  className,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
}) {
  return (
    <button
      {...props}
      disabled={props.disabled || loading}
      className={clsx("button", variant, size, className)}
      aria-busy={loading}
    >
      {loading ? <LoaderCircle className="spin" size={16} /> : null}
      {children}
    </button>
  );
}
export function Input({
  label,
  id,
  ...props
}: InputHTMLAttributes<HTMLInputElement> & { label?: string }) {
  return (
    <label className="field">
      {label && <span>{label}</span>}
      <input id={id} {...props} />
    </label>
  );
}
export function Select({
  label,
  children,
  ...props
}: SelectHTMLAttributes<HTMLSelectElement> & { label: string }) {
  return (
    <label className="field">
      <span>{label}</span>
      <select aria-label={label} {...props}>
        {children}
      </select>
    </label>
  );
}
export function Checkbox(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} type="checkbox" />;
}
export function Radio(props: InputHTMLAttributes<HTMLInputElement>) {
  return <input {...props} type="radio" />;
}
export function Chip({
  active,
  children,
  onClick,
}: {
  active?: boolean;
  children: ReactNode;
  onClick?: () => void;
}) {
  return onClick ? (
    <button
      className={clsx("chip", active && "selected")}
      aria-pressed={active}
      onClick={onClick}
    >
      {children}
    </button>
  ) : (
    <span className="chip">{children}</span>
  );
}
export function Badge({
  children,
  kind = "info",
}: {
  children: ReactNode;
  kind?: string;
}) {
  return (
    <span className="badge" data-kind={kind}>
      {children}
    </span>
  );
}
export function Kbd({ children }: { children: ReactNode }) {
  return <kbd>{children}</kbd>;
}
export function Avatar({ name }: { name: string }) {
  return (
    <span className="avatar" aria-label={name}>
      {name.slice(0, 2).toUpperCase()}
    </span>
  );
}
export function Tooltip({
  text,
  children,
}: {
  text: string;
  children: ReactNode;
}) {
  return (
    <span className="tooltip" tabIndex={0}>
      {children}
      <span role="tooltip">{text}</span>
    </span>
  );
}
export function Modal({
  title,
  children,
  onClose,
  sheet = false,
}: {
  title: string;
  children: ReactNode;
  onClose: () => void;
  sheet?: boolean;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const close = useRef(onClose);
  close.current = onClose;
  const reduced = useReducedMotion();
  useEffect(() => {
    const previous = document.activeElement as HTMLElement;
    const old = document.body.style.overflow;
    const background = document.querySelector(".desktop-app");
    background?.setAttribute("inert", "");
    document.body.style.overflow = "hidden";
    const focusable = () =>
      Array.from(
        ref.current?.querySelectorAll<HTMLElement>(
          'button:not(:disabled),input,select,a[href],[tabindex="0"]',
        ) || [],
      );
    (
      ref.current?.querySelector<HTMLElement>("input") || focusable()[0]
    )?.focus();
    const key = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        close.current();
      }
      if (e.key === "Tab") {
        const els = focusable();
        const first = els[0],
          last = els.at(-1);
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", key);
    return () => {
      document.removeEventListener("keydown", key);
      document.body.style.overflow = old;
      background?.removeAttribute("inert");
      previous?.focus();
    };
  }, []);
  return createPortal(
    <div
      className="backdrop"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <motion.div
        ref={ref}
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className={clsx("modal", sheet && "sheet")}
        variants={reduced ? undefined : scaleIn}
        initial="initial"
        animate="animate"
        exit="exit"
      >
        <div className="modal-title">
          <h2>{title}</h2>
          <Button variant="ghost" onClick={onClose} aria-label="Close dialog">
            <X size={18} />
          </Button>
        </div>
        {children}
      </motion.div>
    </div>,
    document.body,
  );
}
export function Sheet(props: {
  title: string;
  children: ReactNode;
  onClose: () => void;
}) {
  return <Modal {...props} sheet />;
}
export function Popover({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <details className="popover">
      <summary>{label}</summary>
      <div>{children}</div>
    </details>
  );
}
export function Tabs({
  tabs,
  value,
  onChange,
}: {
  tabs: string[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div role="tablist" className="tabs">
      {tabs.map((t, i) => (
        <button
          key={t}
          role="tab"
          aria-selected={value === t}
          tabIndex={value === t ? 0 : -1}
          onClick={() => onChange(t)}
          onKeyDown={(e) => {
            if (["ArrowRight", "ArrowLeft", "Home", "End"].includes(e.key)) {
              e.preventDefault();
              const idx =
                e.key === "Home"
                  ? 0
                  : e.key === "End"
                    ? tabs.length - 1
                    : (i + (e.key === "ArrowRight" ? 1 : -1) + tabs.length) %
                      tabs.length;
              onChange(tabs[idx]);
              (
                e.currentTarget.parentElement?.children[idx] as HTMLElement
              )?.focus();
            }
          }}
        >
          {t}
        </button>
      ))}
    </div>
  );
}
export function ProgressBar({ value }: { value?: number }) {
  return (
    <div
      className={clsx("progress", value === undefined && "indeterminate")}
      role="progressbar"
      aria-label="Progress"
      aria-valuenow={value}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <span style={{ width: value === undefined ? "35%" : `${value}%` }} />
    </div>
  );
}
export class ErrorBoundary extends Component<
  { children: ReactNode },
  { error: string | null }
> {
  state = { error: null as string | null };
  static getDerivedStateFromError(e: Error) {
    return { error: e.message };
  }
  render() {
    return this.state.error ? (
      <div className="empty">
        <AlertTriangle />
        <h1>Unable to display this view</h1>
        <p>{this.state.error}</p>
        <Button
          onClick={() => navigator.clipboard.writeText(this.state.error || "")}
        >
          Copy diagnostics
        </Button>
        <Button onClick={() => location.reload()}>Reload</Button>
      </div>
    ) : (
      this.props.children
    );
  }
}
export function CountUp({ value }: { value: number }) {
  const [shown, setShown] = useState(0);
  const previous = useRef(0);
  const reduced = useReducedMotion();
  useEffect(() => {
    const from = previous.current;
    previous.current = value;
    if (reduced) {
      setShown(value);
      return;
    }
    let frame = 0;
    const start = performance.now();
    const tick = (t: number) => {
      const p = Math.min((t - start) / 600, 1);
      setShown(Math.round(from + (value - from) * (1 - (1 - p) ** 3)));
      if (p < 1) frame = requestAnimationFrame(tick);
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [value, reduced]);
  return <>{shown.toLocaleString()}</>;
}
