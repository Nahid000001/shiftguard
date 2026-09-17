// Must share a hostname with whatever origin the frontend itself is served
// from (both "localhost", or both "127.0.0.1") - browsers treat those two
// hostnames as different *sites* even on the same machine, so a SameSite=Lax
// cookie (the CSRF cookie) set for one is silently refused on a cross-site
// fetch to the other. curl doesn't enforce this, so testing with curl alone
// can't catch it - it only shows up in a real browser.
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown) {
    const detail =
      body && typeof body === "object" && "detail" in body
        ? String((body as { detail: unknown }).detail)
        : `Request failed with status ${status}`;
    super(detail);
    this.status = status;
    this.body = body;
  }
}

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

async function ensureCsrfCookie(): Promise<void> {
  if (getCookie("csrftoken")) return;
  await fetch(`${API_BASE}/api/auth/csrf/`, { credentials: "include" });
}

const SAFE_METHODS = new Set(["GET", "HEAD", "OPTIONS"]);

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const method = (options.method ?? "GET").toUpperCase();
  const headers = new Headers(options.headers);

  if (!SAFE_METHODS.has(method)) {
    await ensureCsrfCookie();
    const token = getCookie("csrftoken");
    if (token) headers.set("X-CSRFToken", token);
  }
  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    method,
    headers,
    credentials: "include",
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new ApiError(response.status, data);
  }
  return data as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body !== undefined ? JSON.stringify(body) : undefined }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PUT", body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  delete: (path: string) => request<void>(path, { method: "DELETE" }),
};

/** Follows a paginated endpoint's `next` links and returns every result. Safe
 * for this app's scale (a single user's data); a truly large dataset would
 * want server-side pagination in the UI instead. */
export async function fetchAllPages<T>(path: string): Promise<T[]> {
  let url: string | null = path;
  const results: T[] = [];
  while (url) {
    const page: { results: T[]; next: string | null } = await request(url);
    results.push(...page.results);
    url = page.next ? page.next.replace(API_BASE, "") : null;
  }
  return results;
}

export { API_BASE, ensureCsrfCookie, getCookie };
