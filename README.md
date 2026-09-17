# ShiftGuard

Multi-agency security shift, pay, and SIA licence tracker. See
`shift-tracker-project-spec.md` for the full project spec and phase plan.

## Stack

Django + Django REST Framework backend, PostgreSQL 16, React + TypeScript
frontend (Vite) in `frontend/`. The backend also still serves a full
Django-templates+htmx UI (Phase 1/2 fallback, kept working) — see "Two
frontends" below.

## Setup

Requires Homebrew, Node, and PostgreSQL (`brew install node postgresql@16`).

Backend:
```bash
brew services start postgresql@16   # if not already running
createdb shiftguard                 # first run only

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # first run only
python manage.py runserver
```

Frontend (separate terminal, needs the backend running):
```bash
cd frontend
npm install
npm run dev
```

Then open http://localhost:5173/ (the React app) or http://127.0.0.1:8000/
(the Django-templates version) — both work against the same backend/database.

Database connection defaults to a local Postgres over the Unix socket as your
OS user (`DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT` env vars
override this — see `shiftguard/settings.py`).

## Two frontends

The React SPA in `frontend/` is now the primary frontend (Phase 3 of the
spec). The original Django-templates+htmx UI is still there and still fully
functional/tested (27+ backend tests cover it) — it wasn't deleted, since
deleting a working, tested UI wasn't something to do unilaterally. Whether to
retire it is an open decision, not a default.

Then open http://127.0.0.1:8000/ and sign in.

## Running tests

```bash
source venv/bin/activate
python manage.py test
```

## API (used by the React frontend)

Every app's CRUD is on the DRF router under `/api/` (agencies, sites, shifts,
licences, expenses), paginated and filterable (date range on shifts/expenses).
Plus:

- `GET /api/dashboard/summary/` — week/month totals, this week's shifts, upcoming licence expiries
- `GET /api/dashboard/charts/` — earnings trend, hours by agency, pay by site
- `GET /api/reports/tax-summary/?year=2026` — UK tax-quarter breakdown (same data as the CSV/PDF export)
- `GET /api/auth/csrf/`, `POST /api/auth/login/`, `POST /api/auth/logout/`, `GET /api/auth/me/` — session-cookie auth for a JS frontend (not token auth)

Everything else requires the Django session cookie (`IsAuthenticated` +
`SessionAuthentication` by default) — log in via `/api/auth/login/` (or
`/accounts/login/` for the Django-templates UI) first. CORS is configured for
a dev frontend on `localhost:5173` (Vite) or `:3000`, with credentials
allowed, so `fetch(url, {credentials: 'include'})` carries the session
cookie across ports. For unsafe methods (POST/PUT/DELETE) the frontend reads
the `csrftoken` cookie and sends it back as the `X-CSRFToken` header — see
`CSRF_TRUSTED_ORIGINS` in `shiftguard/settings.py` if you add another dev
server port.

## App structure

- `agencies` — Agency, Site
- `shifts` — Shift (pay calculation, overnight-shift handling, "duplicate last shift")
- `licences` — Licence (expiry tracking)
- `expenses` — Expense
- `reports` — UK tax-quarter summary (CSV/PDF export)
- `dashboard` — weekly/monthly overview + charts

DRF API mirrors the same models under `/api/`. Every view requires login.

`frontend/` — the React SPA (see `frontend/README.md`).

## Environment notes

Originally built on a machine with no Homebrew, Node, or PostgreSQL — hence
Django templates + htmx + SQLite as the Phase 1 fallback the spec explicitly
allows. Homebrew, Node, and PostgreSQL 16 are now installed and the app runs
on Postgres. The frontend is still Django templates + htmx, not React —
that migration is the one piece of Phase 3 still open. The `dataviz` skill's
`validate_palette.js` for the Charts page can now be run directly (Node is
installed) if the palette or chart surface color ever changes.
