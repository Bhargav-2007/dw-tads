export const number = (n: number) => new Intl.NumberFormat().format(n);
export const shortHash = (s: string, n = 10) =>
  s.length > n * 2 ? `${s.slice(0, n)}…${s.slice(-n)}` : s;
export const relativeTime = (s: string, now = Date.now()) => {
  const t = Date.parse(s);
  if (!Number.isFinite(t)) return "Not reported";
  const seconds = Math.round((t - now) / 1000);
  const [unit, div]: [Intl.RelativeTimeFormatUnit, number] =
    Math.abs(seconds) < 60
      ? ["second", 1]
      : Math.abs(seconds) < 3600
        ? ["minute", 60]
        : Math.abs(seconds) < 86400
          ? ["hour", 3600]
          : ["day", 86400];
  return new Intl.RelativeTimeFormat("en", { numeric: "auto" }).format(
    Math.round(seconds / div),
    unit,
  );
};
export const textValue = (v: unknown): string =>
  v == null
    ? "Not reported"
    : typeof v === "object"
      ? JSON.stringify(v)
      : String(v);
export const safeUrl = (v: string) => {
  try {
    const u = new URL(v);
    return ["https:", "http:"].includes(u.protocol) ? u.href : undefined;
  } catch {
    return undefined;
  }
};
