import type { Config } from "tailwindcss";
const vars = (prefix: string, keys: string[]) =>
  Object.fromEntries(keys.map((k) => [k, `var(--${prefix}-${k})`]));
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: vars("surface", [
          "base",
          "panel",
          "elevated",
          "hover",
          "active",
        ]),
        accent: vars("accent", ["primary", "hover", "muted"]),
        border: vars("border", ["subtle", "default", "strong", "focus"]),
        ink: vars("text", ["primary", "secondary", "tertiary", "inverse"]),
        status: vars("status", [
          "high",
          "medium",
          "low",
          "insufficient",
          "error",
          "info",
        ]),
      },
      spacing: {
        1: "var(--space-1)",
        2: "var(--space-2)",
        3: "var(--space-3)",
        4: "var(--space-4)",
        5: "var(--space-5)",
        6: "var(--space-6)",
        8: "var(--space-8)",
        10: "var(--space-10)",
      },
      fontSize: {
        xs: ["var(--text-xs)", "1.5"],
        sm: ["var(--text-sm)", "1.6"],
        base: ["var(--text-base)", "1.7"],
        lg: ["var(--text-lg)", "1.5"],
        xl: ["var(--text-xl)", "1.3"],
        "2xl": ["var(--text-2xl)", "1.2"],
        "3xl": ["var(--text-3xl)", "1.1"],
      },
      transitionTimingFunction: {
        quint: "var(--ease-out-quint)",
        standard: "var(--ease-in-out)",
        spring: "var(--ease-spring)",
      },
      transitionDuration: {
        fast: "120ms",
        base: "200ms",
        slow: "320ms",
        slower: "480ms",
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
      },
      boxShadow: {
        sm: "var(--shadow-sm)",
        md: "var(--shadow-md)",
        lg: "var(--shadow-lg)",
      },
    },
  },
  plugins: [],
} satisfies Config;
