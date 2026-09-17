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

Requires the Django backend running separately (`python manage.py runserver`
in the parent directory) — see the root README. The dev server runs at
http://localhost:5173/ and talks to Django at `http://127.0.0.1:8000` by
default (override with a `VITE_API_BASE_URL` env var if needed).

Auth is session-cookie based, shared with the Django backend: the app calls
`/api/auth/csrf/` to get a CSRF cookie, then `/api/auth/login/` with that
token, exactly like a same-origin form post would. `credentials: 'include'`
is set on every request so the session cookie round-trips despite the
frontend and backend being on different ports.

## Structure

- `src/api/` — typed fetch client (`client.ts`) and per-resource functions (`resources.ts`)
- `src/auth/` — `AuthContext` (login/logout/session state)
- `src/components/` — shared `Layout`, `ProtectedRoute`, and the generic `CrudList`/`CrudForm` used by Agencies/Sites/Licences/Expenses
- `src/pages/` — one folder per feature; Shifts has a bespoke form (site-rate autofill, duplicate-last-shift) instead of the generic one
- `src/styles/theme.css` — the same dark palette/tokens as the Django templates, so this reads as a continuation of the same product

Tax summary CSV/PDF export are plain links to the Django endpoints
(`/reports/tax-summary/export.{csv,pdf}`) rather than JSON+client-side
download, since they're file downloads, not data to render.

## Verification note

Compiles clean (`npm run build` — TypeScript + Vite), lints clean beyond
stylistic warnings (`npm run lint`), and every module transforms correctly
through Vite's dev server. The actual rendered UI has **not** been visually
verified in a real browser — no browser automation was available in the
session that built this. Click through it yourself before trusting it fully.
