import axios, { AxiosError } from "axios";
import { useToastStore } from "../stores/toastStore";
import type { ApiError } from "../types/api";
export let correlationId = "";
function requestErrorMessage(status: number | undefined, serverMessage?: string) {
  if (status === 403) return "Insufficient permissions";
  if (status === 429) return "Too many requests";
  if (serverMessage) return serverMessage;
  if (!status || status >= 500) return "The analyst API is unavailable. Sign-in requires the backend service on port 8010.";
  if (status === 404) return "The analyst API endpoint was not found. Check the backend configuration.";
  if (status === 401) return "Sign-in was rejected or your session has expired.";
  return "The request could not be completed";
}
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 30000,
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
