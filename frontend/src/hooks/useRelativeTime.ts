import { useSyncExternalStore } from "react";
import { relativeTime } from "../lib/format";
let now = Date.now();
const listeners = new Set<() => void>();
let timer: ReturnType<typeof setInterval> | undefined;
const subscribe = (fn: () => void) => {
  listeners.add(fn);
  if (!timer)
    timer = setInterval(() => {
      now = Date.now();
      listeners.forEach((f) => f());
    }, 60000);
  return () => {
    listeners.delete(fn);
    if (!listeners.size) {
      clearInterval(timer);
      timer = undefined;
    }
  };
};
export function useRelativeTime(s: string) {
  return relativeTime(
    s,
    useSyncExternalStore(subscribe, () => now),
  );
}
