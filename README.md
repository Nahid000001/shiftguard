# ShiftGuard

Multi-agency security shift, pay, and SIA licence tracker. See
`shift-tracker-project-spec.md` for the full project spec and phase plan.

## Stack

Django + Django REST Framework, server-rendered templates + htmx (no Node/build
step for the app itself — Node is installed for future Phase 3 tooling but the
frontend hasn't migrated to React yet), PostgreSQL 16 via Homebrew.

## Setup

Requires Homebrew, Node, and PostgreSQL (`brew install node postgresql@16`).

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

Database connection defaults to a local Postgres over the Unix socket as your
OS user (`DB_NAME`/`DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT` env vars
override this — see `shiftguard/settings.py`).

Then open http://127.0.0.1:8000/ and sign in.

## Running tests

```bash
source venv/bin/activate
python manage.py test
```

## API for a future frontend

Every app's CRUD is on the DRF router under `/api/` (agencies, sites, shifts,
licences, expenses). The data views that were Django-template-only now also
have JSON endpoints, so a separate frontend has everything it needs:

- `GET /api/dashboard/summary/` — week/month totals, this week's shifts, upcoming licence expiries
- `GET /api/dashboard/charts/` — earnings trend, hours by agency, pay by site
- `GET /api/reports/tax-summary/?year=2026` — UK tax-quarter breakdown (same data as the CSV/PDF export)

All of it requires the Django session cookie (`IsAuthenticated` + `SessionAuthentication`
by default) — log in via `/accounts/login/` first. CORS is configured for a
React dev server on `localhost:5173` (Vite) or `:3000`, with credentials
allowed, so `fetch(url, {credentials: 'include'})` from a separately-run
frontend will carry the session cookie. For unsafe methods (POST/PUT/DELETE)
the frontend needs to read the `csrftoken` cookie and send it back as the
`X-CSRFToken` header — see `CSRF_TRUSTED_ORIGINS` in `shiftguard/settings.py`
if you add another dev server port.

## App structure

- `agencies` — Agency, Site
- `shifts` — Shift (pay calculation, overnight-shift handling, "duplicate last shift")
- `licences` — Licence (expiry tracking)
- `expenses` — Expense
- `reports` — UK tax-quarter summary (CSV/PDF export)
- `dashboard` — weekly/monthly overview + charts

DRF API mirrors the same models under `/api/`. Every view requires login.

## Environment notes

Originally built on a machine with no Homebrew, Node, or PostgreSQL — hence
Django templates + htmx + SQLite as the Phase 1 fallback the spec explicitly
allows. Homebrew, Node, and PostgreSQL 16 are now installed and the app runs
on Postgres. The frontend is still Django templates + htmx, not React —
that migration is the one piece of Phase 3 still open. The `dataviz` skill's
`validate_palette.js` for the Charts page can now be run directly (Node is
installed) if the palette or chart surface color ever changes.
