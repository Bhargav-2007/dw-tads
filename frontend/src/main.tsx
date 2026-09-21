import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { MotionConfig } from "framer-motion";
import App from "./App";
import { ErrorBoundary } from "./components/ui";
import { useAuthStore } from "./stores/authStore";
import "./styles/fonts.css";
import "./styles/tokens.css";
import "./styles/globals.css";
useAuthStore.getState().initialize();
ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <MotionConfig reducedMotion="user">
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </MotionConfig>
    </ErrorBoundary>
  </React.StrictMode>,
);
