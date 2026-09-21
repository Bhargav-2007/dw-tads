import { create } from "zustand";
import { api } from "../lib/api";
import type { AuthResponse } from "../types/api";
export function decodeUser(token: string) {
  try {
    const part = token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
    const p = JSON.parse(atob(part));
    return {
      username: String(p.username || p.sub || "Analyst"),
      role: String(p.role || "analyst"),
      exp: Number(p.exp || 0),
    };
  } catch {
    return null;
  }
}
interface AuthState {
  token: string | null;
  user: { username: string; role: string } | null;
  login: (username: string, password: string, totp: string) => Promise<void>;
  logout: () => void;
  initialize: () => void;
}
export const useAuthStore = create<AuthState>((set) => ({
  token: null,
  user: null,
  login: async (username, password, totp) => {
    const { data } = await api.post<AuthResponse>("/auth/token", {
      username,
      password,
      totp,
    });
    if (!data.access_token)
      throw new Error("The API did not return an access token");
    sessionStorage.setItem("dwtds_token", data.access_token);
    sessionStorage.setItem(
      "dwtds_expires",
      String(Date.now() + data.expires_in * 1000),
    );
    set({
      token: data.access_token,
      user: decodeUser(data.access_token) || { username, role: "analyst" },
    });
  },
  logout: () => {
    sessionStorage.removeItem("dwtds_token");
    sessionStorage.removeItem("dwtds_expires");
    set({ token: null, user: null });
  },
  initialize: () => {
    const token = sessionStorage.getItem("dwtds_token");
    const user = token ? decodeUser(token) : null;
    const expires = Number(sessionStorage.getItem("dwtds_expires") || 0);
    if (
      token &&
      expires > Date.now() &&
      (!user?.exp || user.exp * 1000 > Date.now())
    )
      set({ token, user: user || { username: "Analyst", role: "analyst" } });
    else {
      sessionStorage.removeItem("dwtds_token");
      sessionStorage.removeItem("dwtds_expires");
      set({ token: null, user: null });
    }
  },
}));
