import { useState } from "react";
import { Navigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Shield, Eye, EyeOff, ArrowRight, LockKeyhole } from "lucide-react";
import { Button, Input } from "../components/ui";
import { useAuthStore } from "../stores/authStore";
import { errorMessage } from "../lib/api";
import { useReducedMotion } from "../hooks/useReducedMotion";
export default function Login() {
  const { token, login } = useAuthStore();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [totp, setTotp] = useState("");
  const [show, setShow] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  const [attempt, setAttempt] = useState(0);
  const reduced = useReducedMotion();
  if (token) return <Navigate to="/timeline" replace />;
  return (
    <div className="login-page" role="main">
      <div className="login-context">
        <Shield size={24} />
        <span>DW-TADS / SECURE ANALYST ACCESS</span>
      </div>
      <motion.form
        key={attempt}
        className="login-card"
        initial={{ opacity: 0, scale: reduced ? 1 : 0.96 }}
        animate={{
          opacity: 1,
          scale: 1,
          x: !reduced && error ? [0, -4, 4, -4, 4, 0] : 0,
        }}
        transition={{ duration: 0.3 }}
        onSubmit={async (e) => {
          e.preventDefault();
          setPending(true);
          setError("");
          try {
            await login(username, password, totp);
          } catch (err) {
            setError(errorMessage(err));
            setAttempt((a) => a + 1);
          } finally {
            setPending(false);
          }
        }}
      >
        <div className="login-mark">
          <Shield size={42} />
        </div>
        <h1>DW-TADS</h1>
        <p className="login-subtitle">Analyst Access</p>
        <div className="login-rule" />
        <Input
          label="Username"
          autoComplete="username"
          value={username}
          required
          onChange={(e) => setUsername(e.target.value)}
        />
        <div className="password-field">
          <Input
            label="Password"
            type={show ? "text" : "password"}
            autoComplete="current-password"
            value={password}
            required
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button
            type="button"
            variant="ghost"
            aria-label={show ? "Hide password" : "Show password"}
            onClick={() => setShow((v) => !v)}
          >
            {show ? <EyeOff size={17} /> : <Eye size={17} />}
          </Button>
        </div>
        <Input
          label="Authenticator code"
          className="mono totp"
          placeholder="123 456"
          value={totp}
          inputMode="numeric"
          autoComplete="one-time-code"
          pattern="[0-9]{6}"
          maxLength={6}
          required
          onChange={(e) =>
            setTotp(e.target.value.replace(/\D/g, "").slice(0, 6))
          }
        />
        <p className="muted text-xs">
          Enter the 6-digit code from your authenticator.
        </p>
        <Button
          type="submit"
          variant="primary"
          size="lg"
          loading={pending}
          className="full"
        >
          Sign in
          <ArrowRight size={17} />
        </Button>
        <div className="login-error" role="alert">
          {error}
        </div>
        {import.meta.env.VITE_DEMO_MODE === "true" && (
          <p className="muted">
            Generate the current TOTP with your demo account’s provisioned
            authenticator. No demo secret is bundled in this app.
          </p>
        )}
        <div className="login-foot">
          <LockKeyhole size={14} />
          Authorized personnel only
        </div>
      </motion.form>
      <p className="login-bottom">DARK WEB THREAT ACTOR DETECTION SYSTEM</p>
    </div>
  );
}
