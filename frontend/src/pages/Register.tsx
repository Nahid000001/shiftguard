import { useState } from "react";
import type { FormEvent } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import { GoogleSignInButton } from "../components/GoogleSignInButton";
import { PasswordInput } from "../components/PasswordInput";

interface FieldErrors {
  username?: string[];
  password?: string[];
  detail?: string;
}

export function Register() {
  const { username: loggedInAs, loading, register, setAuthenticatedUsername } = useAuth();
  const [usernameInput, setUsernameInput] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState<FieldErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  if (!loading && loggedInAs) {
    return <Navigate to="/" replace />;
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setErrors({});
    setSubmitting(true);
    try {
      await register(usernameInput, password, email || undefined);
      navigate("/", { replace: true });
    } catch (err) {
      if (err instanceof ApiError && err.body && typeof err.body === "object") {
        setErrors(err.body as FieldErrors);
      } else {
        setErrors({ detail: "Could not reach the server." });
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>Create an account</h1>
        <form onSubmit={handleSubmit}>
          {errors.detail && <p style={{ color: "var(--danger)", fontSize: "0.85rem" }}>{errors.detail}</p>}
          <div className="field">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              value={usernameInput}
              onChange={(e) => setUsernameInput(e.target.value)}
              autoFocus
              required
            />
            {errors.username?.map((msg) => (
              <p key={msg} style={{ color: "var(--danger)", fontSize: "0.8rem", margin: "0.25rem 0 0" }}>
                {msg}
              </p>
            ))}
          </div>
          <div className="field">
            <label htmlFor="email">Email (optional)</label>
            <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <PasswordInput id="password" value={password} onChange={setPassword} autoComplete="new-password" required />
            {errors.password?.map((msg) => (
              <p key={msg} style={{ color: "var(--danger)", fontSize: "0.8rem", margin: "0.25rem 0 0" }}>
                {msg}
              </p>
            ))}
          </div>
          <button type="submit" className="btn" style={{ width: "100%" }} disabled={submitting}>
            {submitting ? "Creating account…" : "Create account"}
          </button>
        </form>
        <div style={{ margin: "1rem 0", display: "flex", justifyContent: "center" }}>
          <GoogleSignInButton
            onSuccess={(u) => {
              setAuthenticatedUsername(u);
              navigate("/", { replace: true });
            }}
            onError={(msg) => setErrors({ detail: msg })}
          />
        </div>
        <p style={{ marginTop: "1rem", textAlign: "center", fontSize: "0.85rem", color: "var(--muted)" }}>
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
