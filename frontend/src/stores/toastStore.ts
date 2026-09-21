import { create } from "zustand";
export interface Toast {
  id: string;
  message: string;
  kind: "success" | "error" | "info" | "warning";
  detail?: string;
  retry?: () => void;
  retryAt?: number;
}
export const useToastStore = create<{
  toasts: Toast[];
  push: (t: Omit<Toast, "id">) => void;
  dismiss: (id: string) => void;
}>((set) => ({
  toasts: [],
  push: (t) =>
    set((s) => ({
      toasts: [...s.toasts.slice(-3), { ...t, id: crypto.randomUUID() }],
    })),
  dismiss: (id) =>
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));
