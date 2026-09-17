import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { api, ApiError } from "../api/client";

interface AuthState {
  username: string | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, password: string, email?: string) => Promise<void>;
  logout: () => Promise<void>;
  /** For a login completed elsewhere (e.g. the Google button already set the
   * session cookie itself) - just syncs local state to match. */
  setAuthenticatedUsername: (username: string) => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [username, setUsername] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get<{ username: string }>("/api/auth/me/")
      .then((res) => setUsername(res.username))
      .catch(() => setUsername(null))
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (usernameInput: string, password: string) => {
    try {
      const res = await api.post<{ username: string }>("/api/auth/login/", {
        username: usernameInput,
        password,
      });
      setUsername(res.username);
    } catch (err) {
      if (err instanceof ApiError) throw err;
      throw new ApiError(0, { detail: "Could not reach the server." });
    }
  }, []);

  const register = useCallback(async (usernameInput: string, password: string, email?: string) => {
    try {
      const res = await api.post<{ username: string }>("/api/auth/register/", {
        username: usernameInput,
        password,
        email,
      });
      setUsername(res.username);
    } catch (err) {
      if (err instanceof ApiError) throw err;
      throw new ApiError(0, { detail: "Could not reach the server." });
    }
  }, []);

  const logout = useCallback(async () => {
    await api.post("/api/auth/logout/");
    setUsername(null);
  }, []);

  const value = useMemo(
    () => ({ username, loading, login, register, logout, setAuthenticatedUsername: setUsername }),
    [username, loading, login, register, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
