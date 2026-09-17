import { useEffect, useRef } from "react";
import { api, ApiError, resetCsrfToken } from "../api/client";

// No official type package is pulled in just for this one script's shape.
declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: {
            client_id: string;
            callback: (response: { credential: string }) => void;
          }) => void;
          renderButton: (parent: HTMLElement, options: Record<string, unknown>) => void;
        };
      };
    };
  }
}

let scriptPromise: Promise<void> | null = null;

function loadGoogleScript(): Promise<void> {
  if (scriptPromise) return scriptPromise;
  scriptPromise = new Promise((resolve, reject) => {
    if (window.google?.accounts?.id) {
      resolve();
      return;
    }
    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error("Failed to load Google Identity Services"));
    document.head.appendChild(script);
  });
  return scriptPromise;
}

interface GoogleSignInButtonProps {
  onSuccess: (username: string) => void;
  onError: (message: string) => void;
  /** Google's button label - "signin_with" (default) renders "Sign in with
   * Google", "signup_with" renders "Sign up with Google". Purely cosmetic -
   * the endpoint behaves identically either way (finds-or-creates by email),
   * but showing "Sign in" on a Register page is confusingly worded. */
  text?: "signin_with" | "signup_with" | "continue_with" | "signin";
}

/** Renders nothing if VITE_GOOGLE_CLIENT_ID isn't set, rather than a button
 * that's guaranteed to fail - see frontend/README.md for how to set it up. */
export function GoogleSignInButton({ onSuccess, onError, text = "signin_with" }: GoogleSignInButtonProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;

  useEffect(() => {
    if (!clientId || !containerRef.current) return;
    let cancelled = false;

    loadGoogleScript()
      .then(() => {
        if (cancelled || !containerRef.current || !window.google) return;
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: async (response) => {
            try {
              const res = await api.post<{ username: string }>("/api/auth/google/", {
                credential: response.credential,
              });
              resetCsrfToken(); // Django rotates the CSRF token on login
              onSuccess(res.username);
            } catch (err) {
              onError(err instanceof ApiError ? err.message : "Google sign-in failed.");
            }
          },
        });
        window.google.accounts.id.renderButton(containerRef.current, {
          theme: "outline",
          size: "large",
          width: 296,
          text,
        });
      })
      .catch(() => onError("Could not load Google sign-in."));

    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clientId, text]);

  if (!clientId) return null;

  return <div ref={containerRef} />;
}
