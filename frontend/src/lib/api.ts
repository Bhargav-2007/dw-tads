import axios, {
  AxiosError,
  type InternalAxiosRequestConfig,
  type AxiosResponse,
} from "axios";
import { useToastStore } from "../stores/toastStore";
import type { ApiError } from "../types/api";
import {
  getDemoActor,
  getDemoAudit,
  getDemoGraph,
  getDemoSources,
  getDemoTimeline,
  DEMO_METRICS,
} from "./demoData";

export let correlationId = "";

export function isDemoMode(): boolean {
  if (typeof window === "undefined") return false;
  if (import.meta.env.VITE_DEMO_MODE === "true") return true;
  if (window.location.hostname.endsWith(".github.io")) return true;
  if (sessionStorage.getItem("dwtds_demo_mode") === "true") return true;
  return false;
}

function createDemoJwt(username: string, role: string): string {
  const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }));
  const payload = btoa(
    JSON.stringify({
      sub: username,
      username: username,
      role: role,
      exp: Math.floor(Date.now() / 1000) + 86400 * 7,
      iat: Math.floor(Date.now() / 1000),
    }),
  );
  return `${header}.${payload}.demo_signature`;
}

function requestErrorMessage(
  status: number | undefined,
  serverMessage?: string,
) {
  if (status === 403) return "Insufficient permissions";
  if (status === 429) return "Too many requests";
  if (serverMessage) return serverMessage;
  if (!status || status >= 500)
    return "The analyst API is unavailable. Sign-in requires the backend service on port 8010.";
  if (status === 404)
    return "The analyst API endpoint was not found. Check the backend configuration.";
  if (status === 401)
    return "Sign-in was rejected or your session has expired.";
  return "The request could not be completed";
}

const defaultAdapter = axios.getAdapter(axios.defaults.adapter);

async function handleDemoRequest(
  config: InternalAxiosRequestConfig,
): Promise<AxiosResponse> {
  const url = config.url || "";
  const cleanPath = url.replace(/^(https?:\/\/[^/]+)?(\/api)?/, "");

  if (cleanPath.startsWith("/auth/token")) {
    let body: { username?: string; password?: string } = {};
    try {
      body =
        typeof config.data === "string"
          ? JSON.parse(config.data)
          : config.data || {};
    } catch {}
    const username = body.username || "analyst1";
    const role = username.toLowerCase().includes("admin") ? "admin" : "analyst";
    const token = createDemoJwt(username, role);
    return {
      data: {
        access_token: token,
        token_type: "bearer",
        expires_in: 86400 * 7,
      },
      status: 200,
      statusText: "OK",
      headers: { "x-correlation-id": "demo-auth" },
      config,
    };
  }

  if (cleanPath.startsWith("/query/timeline")) {
    const data = getDemoTimeline(config.params);
    return {
      data,
      status: 200,
      statusText: "OK",
      headers: {
        "x-correlation-id": "demo-timeline",
        "x-result-hash": data.result_hash,
      },
      config,
    };
  }

  if (cleanPath.startsWith("/query/actor/")) {
    const actorId = decodeURIComponent(
      cleanPath.replace(/^\/query\/actor\//, "").split("?")[0] ||
        "ACTOR-HYDRA-09",
    );
    const data = getDemoActor(actorId);
    return {
      data,
      status: 200,
      statusText: "OK",
      headers: {
        "x-correlation-id": "demo-actor",
        "x-result-hash": data.result_hash,
      },
      config,
    };
  }

  if (cleanPath.startsWith("/query/graph")) {
    let actorId: string | undefined = undefined;
    if (config.params?.actor_id) {
      actorId = String(config.params.actor_id);
    } else {
      const match = cleanPath.match(/actor_id=([^&]+)/);
      if (match) actorId = decodeURIComponent(match[1]);
    }
    const data = getDemoGraph(actorId);
    return {
      data,
      status: 200,
      statusText: "OK",
      headers: {
        "x-correlation-id": "demo-graph",
        "x-result-hash": data.result_hash,
      },
      config,
    };
  }

  if (cleanPath.startsWith("/query/sources")) {
    const data = getDemoSources();
    return {
      data,
      status: 200,
      statusText: "OK",
      headers: {
        "x-correlation-id": "demo-sources",
        "x-result-hash": data.result_hash,
      },
      config,
    };
  }

  if (cleanPath.startsWith("/query/audit")) {
    const data = getDemoAudit();
    return {
      data,
      status: 200,
      statusText: "OK",
      headers: {
        "x-correlation-id": "demo-audit",
        "x-result-hash": data.result_hash,
      },
      config,
    };
  }

  if (cleanPath.startsWith("/export")) {
    let body: { format?: string; query_id?: string } = {};
    try {
      body =
        typeof config.data === "string"
          ? JSON.parse(config.data)
          : config.data || {};
    } catch {}
    const format = body.format || "json";
    let content: string;
    let mime = "application/json";
    if (format === "csv") {
      mime = "text/csv";
      content = `actor_id,risk_score,tier,confidence,category,last_seen\nACTOR-HYDRA-09,0.94,HIGH,0.96,"ransomware,hacking",2026-09-21T18:00:00Z\nSHADOW-BROKER-X,0.88,HIGH,0.91,"cyber_espionage,exploit_broker",2026-09-21T16:30:00Z\nFIN-EXTORTION-4,0.74,MEDIUM,0.82,"carding,money_laundering",2026-09-21T12:00:00Z\n`;
    } else if (format === "pdf") {
      mime = "application/pdf";
      content = `%PDF-1.4\n% DW-TADS Intelligence Dossier Report\nQuery ID: ${body.query_id || "demo"}\nGenerated: ${new Date().toISOString()}\n`;
    } else {
      content = JSON.stringify(getDemoTimeline(), null, 2);
    }
    const blob = new Blob([content], { type: mime });
    return {
      data: blob,
      status: 200,
      statusText: "OK",
      headers: {
        "content-disposition": `attachment; filename="dw-tads-${body.query_id || "export"}.${format}"`,
        "x-result-hash": "demo-result-hash-" + Math.random().toString(36).slice(2),
        "x-correlation-id": "demo-export",
      },
      config,
    };
  }

  if (cleanPath.startsWith("/health")) {
    return {
      data: { status: "ok", mode: "showcase" },
      status: 200,
      statusText: "OK",
      headers: { "x-correlation-id": "demo-health" },
      config,
    };
  }

  if (cleanPath.startsWith("/ready")) {
    return {
      data: { status: "ready" },
      status: 200,
      statusText: "OK",
      headers: { "x-correlation-id": "demo-ready" },
      config,
    };
  }

  if (cleanPath.startsWith("/metrics")) {
    return {
      data: DEMO_METRICS,
      status: 200,
      statusText: "OK",
      headers: {
        "content-type": "text/plain; version=0.0.4",
        "x-correlation-id": "demo-metrics",
      },
      config,
    };
  }

  return {
    data: { status: "ok" },
    status: 200,
    statusText: "OK",
    headers: {},
    config,
  };
}

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 30000,
  adapter: async (config) => {
    if (isDemoMode()) {
      return handleDemoRequest(config);
    }
    try {
      return await defaultAdapter(config);
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && !err.response && typeof window !== "undefined") {
        sessionStorage.setItem("dwtds_demo_mode", "true");
        return handleDemoRequest(config);
      }
      throw err;
    }
  },
});

api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem("dwtds_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => {
    correlationId = r.headers["x-correlation-id"] || "";
    return r;
  },
  async (error: AxiosError<ApiError>) => {
    if (axios.isCancel(error)) return Promise.reject(error);
    if (error.response?.data instanceof Blob) {
      try {
        error.response.data = JSON.parse(await error.response.data.text());
      } catch {}
    }
    const status = error.response?.status;
    const raw = error.response?.headers["retry-after"];
    const seconds = raw ? Number(raw) : 0;
    const retryAt = raw
      ? Number.isFinite(seconds)
        ? Date.now() + seconds * 1000
        : Date.parse(raw)
      : undefined;
    const message = requestErrorMessage(status, error.response?.data?.error);
    if (status === 401) {
      sessionStorage.removeItem("dwtds_token");
      sessionStorage.removeItem("dwtds_expires");
      window.dispatchEvent(new Event("dwtds:unauthorized"));
    }
    useToastStore.getState().push({
      message,
      kind: "error",
      detail: error.response?.data?.correlation_id,
      retryAt,
      retry:
        !error.response && error.config?.method === "get"
          ? () => {
              window.dispatchEvent(new Event("dwtds:retry"));
            }
          : undefined,
    });
    return Promise.reject(error);
  },
);

export const errorMessage = (e: unknown) =>
  axios.isAxiosError(e)
    ? requestErrorMessage(e.response?.status, e.response?.data?.error)
    : e instanceof Error
      ? e.message
      : "Unexpected error";

export function downloadBlob(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

export async function exportQuery(
  queryId: string,
  format: "csv" | "json" | "pdf",
) {
  const response = await api.post(
    "/export",
    { query_id: queryId, format },
    { responseType: "blob" },
  );
  const disposition = String(response.headers["content-disposition"] || "");
  const match = /filename="?([^";]+)"?/i.exec(disposition);
  const filename =
    match?.[1]?.replace(/[\\/]/g, "_") || `dw-tads-${queryId}.${format}`;
  downloadBlob(response.data, filename);
  useToastStore.getState().push({
    kind: "success",
    message: `${format.toUpperCase()} export downloaded`,
    detail: response.headers["x-result-hash"],
  });
}