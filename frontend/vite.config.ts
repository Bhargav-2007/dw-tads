import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  base: process.env.BASE_URL ?? (process.env.NODE_ENV === "production" ? "/dw-tads/" : "/"),
  plugins: [react()],
  server: {
    port: 5173,
    watch: { usePolling: process.env.CHOKIDAR_USEPOLLING === "true", interval: 500 },
    strictPort: true,
    proxy: {
      "/api": {
        target: "http://localhost:8010",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ""),
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          react: ["react", "react-dom", "react-router-dom"],
          graph: ["cytoscape", "cytoscape-cose-bilkent"],
          charts: ["recharts"],
          motion: ["framer-motion"],
        },
      },
    },
  },
});