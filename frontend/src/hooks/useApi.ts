import { useCallback, useEffect, useState } from "react";
import axios from "axios";
import { api, errorMessage } from "../lib/api";
export function useApi<T>(path: string | null) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(Boolean(path));
  const [error, setError] = useState<string | null>(null);
  const [version, setVersion] = useState(0);
  const refresh = useCallback(() => setVersion((v) => v + 1), []);
  useEffect(() => {
    if (!path) {
      setLoading(false);
      return;
    }
    const controller = new AbortController();
    setData(null);
    setLoading(true);
    setError(null);
    api
      .get<T>(path, { signal: controller.signal })
      .then((r) => setData(r.data))
      .catch((e) => {
        if (!axios.isCancel(e)) setError(errorMessage(e));
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, [path, version]);
  useEffect(() => {
    window.addEventListener("dwtds:retry", refresh);
    return () => window.removeEventListener("dwtds:retry", refresh);
  }, [refresh]);
  return { data, loading, error, refresh };
}
