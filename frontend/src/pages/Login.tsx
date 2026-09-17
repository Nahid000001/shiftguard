import { useState } from "react";
import type { FormEvent } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { API_BASE, ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { GoogleSignInButton } from "../components/GoogleSignInButton";
import { PasswordInput } from "../components/PasswordInput";

export function Login() {
  const { username, loading, login, setAuthenticatedUsername } = useAuth();
  const [usernameInput, setUsernameInput] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  if (!loading && username) {
    const from = (location.state as { from?: string })?.from ?? "/";
    return <Navigate to={from} replace />;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(usernameInput, password);
      navigate("/", { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.status === 400) {
        setError("Invalid username or password.");
      } else if (err instanceof ApiError) {
        // Anything other than a real "wrong credentials" response (CSRF
        // failure, network error, misconfigured API host, ...) - don't lie
        // and call it a bad password when it might not be.
        setError(`Sign-in failed (${err.status}): ${err.message}`);
      } else {
        setError("Could not reach the server.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>ShiftGuard</h1>
        <form onSubmit={handleSubmit}>
          {error && <p style={{ color: "var(--danger)", fontSize: "0.85rem" }}>{error}</p>}
          <div className="field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              value={usernameInput}
              onChange={(e) => setUsernameInput(e.target.value)}
              autoFocus
              required
            />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <PasswordInput
              id="password"
              value={password}
              onChange={setPassword}
              autoComplete="current-password"
              required
            />
          </div>
          <button type="submit" className="btn" style={{ width: "100%" }} disabled={submitting}>
            {submitting ? "Signing in…" : "Sign in"}
          </button>
        </form>
        <p style={{ marginTop: "0.75rem", textAlign: "center", fontSize: "0.85rem" }}>
          <a href={`${API_BASE}/accounts/password-reset/`}>Forgot your password?</a>
        </p>
        <div style={{ margin: "1rem 0", display: "flex", justifyContent: "center" }}>
          <GoogleSignInButton
            onSuccess={(u) => {
              setAuthenticatedUsername(u);
              navigate("/", { replace: true });
            }}
            onError={setError}
          />
        </div>
        <p style={{ marginTop: "1rem", textAlign: "center", fontSize: "0.85rem", color: "var(--muted)" }}>
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}
