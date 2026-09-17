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
functional/tested (70+ backend tests cover it) — it wasn't deleted, since
deleting a working, tested UI wasn't something to do unilaterally. Whether to
retire it is an open decision, not a default.

## Accounts: multi-user, registration, Google sign-in

This is now a real multi-user app, not a single-operator tool — every
Agency/Licence/Expense has a direct owner, and Site/Shift ownership derives
through Agency. Every view and API endpoint is scoped to `request.user`;
cross-account access (viewing, editing, or attaching a record to someone
else's agency) is rejected, not just hidden — see the isolation tests in each
app's `tests.py` for exactly what's covered.

New users can self-register three ways, all landing in the same account:
- `/accounts/register/` (Django-templates UI) or the Register page in the
  React app — both take username + password, with an optional email
- `POST /api/auth/register/` directly
- "Sign in with Google" (see below) — creates an account automatically on
  first use, matched/created by email, with no local password

**Email verification.** Registering with an email doesn't just trust it —
you get a one-time link (printed to the console by default; see "Real email
delivery" below) to prove you own it. This matters because of how Google
sign-in matches accounts: it looks up an existing user by email, and if
nobody had to prove ownership of that email, anyone could register with
*your* address first and get logged into by your Google sign-in later.
`accounts/services.py`'s `get_or_create_google_user` only links to an
existing account if its email is verified — otherwise it creates a brand
new account, so a squatted, unverified email can never intercept the real
owner's Google sign-in (see `accounts/tests.py` for the exact scenario this
is tested against, including a full end-to-end run through the real
endpoint with only the Google token verification mocked).

**Real email delivery** (optional — defaults to printing to the console,
which is fine for solo/dev use): set `EMAIL_BACKEND`,
`EMAIL_HOST`/`EMAIL_PORT`/`EMAIL_HOST_USER`/`EMAIL_HOST_PASSWORD`/
`EMAIL_USE_TLS`, and `DEFAULT_FROM_EMAIL` env vars for a real SMTP provider
(SendGrid, Mailgun, SES, etc.) — see `shiftguard/settings.py`.

**Google sign-in setup** (the one piece that needs your action — creating
OAuth credentials requires your own Google account, so this can't be done
for you):

1. Go to [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials
2. Create an OAuth 2.0 Client ID, application type **Web application**
3. Under "Authorized JavaScript origins" add `http://localhost:5173` (and `http://localhost:8000` if you want the button on the Django-templates login page too)
4. Copy the generated **Client ID** (looks like `xxxxx.apps.googleusercontent.com`) — no client secret is needed, this uses ID-token verification, not the authorization-code flow
5. Set it in **two** places (same value, both are safe to be public — the Client ID isn't a secret):
   - Backend: `GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com` in your shell env before `runserver`
   - Frontend: create `frontend/.env.local` with `VITE_GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com`

Without this, the "Sign in with Google" button simply doesn't render (checked
via `if (!clientId) return null`) — everything else works normally.

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
- `GET /api/auth/csrf/`, `POST /api/auth/login/`, `POST /api/auth/register/`, `POST /api/auth/google/`, `POST /api/auth/logout/`, `GET /api/auth/me/` — session-cookie auth for a JS frontend (not token auth)

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

- `accounts` — EmailVerification, the Google sign-in trust check, verify-email link view
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
allows. Homebrew, Node, and PostgreSQL 16 are now installed, the app runs on
Postgres, and the React frontend (Phase 3) is built — see "Two frontends"
above. The `dataviz` skill's `validate_palette.js` for the Charts page can be
run directly (Node is installed) if the palette or chart surface color ever
changes.
