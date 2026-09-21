import { useReducedMotion as usePreference } from "framer-motion";
import { useFocusStore } from "../stores/focusStore";
export function useReducedMotion() {
  return Boolean(usePreference() || useFocusStore((s) => s.focusMode));
}
