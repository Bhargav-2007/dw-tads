import { create } from "zustand";
export const useFocusStore = create<{
  focusMode: boolean;
  zenMode: boolean;
  sound: boolean;
  toggle: () => void;
  setZen: (v: boolean) => void;
  setSound: (v: boolean) => void;
}>((set) => ({
  focusMode: false,
  zenMode: false,
  sound: false,
  toggle: () => set((s) => ({ focusMode: !s.focusMode })),
  setZen: (zenMode) => set({ zenMode }),
  setSound: (sound) => set({ sound }),
}));
