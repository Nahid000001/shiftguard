# ShiftGuard frontend

React + TypeScript SPA (Vite) consuming the Django REST Framework API in
`../` (the parent Django project). This replaces the Django-templates+htmx
frontend as ShiftGuard's primary UI (see the root README's "Environment
notes" for that history).

## Setup

```bash
npm install
npm run dev
```

Requires the Django backend running separately (`python manage.py runserver
localhost:8000` in the parent directory) — see the root README. The dev
server runs at http://localhost:5173/ and talks to Django at
`http://localhost:8000` by default (override with a `VITE_API_BASE_URL` env
var if needed). **Use `localhost` for both, not a mix with `127.0.0.1`** —
browsers treat those as different *sites*, so a SameSite=Lax cookie (the CSRF
cookie) set for one is silently refused on a cross-site fetch to the other.
This isn't a hypothetical: it's exactly what broke login the first time this
was tested in a real browser (curl-based testing didn't catch it, since curl
doesn't enforce SameSite).

Auth is session-cookie based, shared with the Django backend: the app calls
`/api/auth/csrf/` to get a CSRF cookie, then `/api/auth/login/` (or
`/api/auth/register/`, or `/api/auth/google/`) with that token, exactly like
a same-origin form post would. `credentials: 'include'` is set on every
request so the session cookie round-trips despite the frontend and backend
being on different ports. Every account's data is isolated - see the root
README's "Accounts" section for registration and Google sign-in setup.

## Structure

- `src/api/` — typed fetch client (`client.ts`) and per-resource functions (`resources.ts`)
- `src/auth/` — `AuthContext` (login/register/logout/session state)
- `src/components/` — shared `Layout`, `ProtectedRoute`, `PasswordInput` (show/hide toggle), `GoogleSignInButton` (renders nothing if `VITE_GOOGLE_CLIENT_ID` isn't set), and the generic `CrudList`/`CrudForm` used by Agencies/Sites/Licences/Expenses
- `src/pages/` — one folder per feature; Login and Register both offer Google sign-in; Shifts has a bespoke form (site-rate autofill, duplicate-last-shift) instead of the generic one
- `src/pages/Landing.tsx` — the public marketing home
- `src/styles/theme.css` — the same dark palette/tokens as the Django templates, so this reads as a continuation of the same product

## PWA (installable on iOS/Android)

`vite-plugin-pwa` (configured in `vite.config.ts`) generates the manifest and
service worker at build time - nothing to run manually, `npm run build`
produces `dist/manifest.webmanifest`, `dist/sw.js`. Icons are in
`public/icons/` - currently a plain placeholder ("SG" monogram, generated
with Pillow since there's no real logo yet); swap those four PNGs for real
branding whenever you have one, same filenames. Only precaches the app shell
(JS/CSS/HTML/icons) - API responses are per-user and session-sensitive, so
they're deliberately never cached by the service worker. See the root
README's "Installing on iOS" section for the actual install steps once
deployed - `npm run dev` does not register the service worker (only
production builds do), so this can't be tested via the dev server.

## Routing

`/` is public: a signed-out visitor sees the landing page, a signed-in one is
redirected straight to `/dashboard` (`HomeRoute` in `App.tsx` makes that
call). Everything else under `ProtectedRoute` needs a session; it's sent to
`/login` with the originally-requested path preserved in navigation state, so
signing in returns you to where you were headed rather than always dropping
you at the dashboard.

Tax summary CSV/PDF export are plain links to the Django endpoints
(`/reports/tax-summary/export.{csv,pdf}`) rather than JSON+client-side
download, since they're file downloads, not data to render.

## Verification note

The core app (login, dashboard, shifts, charts, tax summary, CRUD) has been
confirmed working end-to-end in a real browser. The newer additions -
registration page, password show/hide toggle, Google sign-in button, the
public landing page and the `/` vs `/dashboard` routing split - have **not**
yet been browser-verified, same caveat as before: no browser automation was
available in the session that built them, only TypeScript compiling clean
and the backend contracts being tested directly. Click through those
specifically before trusting them.
