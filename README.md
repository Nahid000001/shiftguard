# ShiftGuard

Multi-agency security shift, pay, and SIA licence tracker. See
`shift-tracker-project-spec.md` for the full project spec and phase plan.

## Stack

Django + Django REST Framework, server-rendered templates + htmx (no Node/build
step), SQLite for now. This is a deliberate substitution for the spec's
React + Postgres plan — see "Environment notes" below.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # first run only
python manage.py runserver
```

Then open http://127.0.0.1:8000/ and sign in.

## Running tests

```bash
source venv/bin/activate
python manage.py test
```

## App structure

- `agencies` — Agency, Site
- `shifts` — Shift (pay calculation, overnight-shift handling, "duplicate last shift")
- `licences` — Licence (expiry tracking)
- `expenses` — Expense
- `reports` — UK tax-quarter summary (CSV/PDF export)
- `dashboard` — weekly/monthly overview + charts

DRF API mirrors the same models under `/api/`. Every view requires login.

## Environment notes

Built on a machine with no Homebrew, Node, or PostgreSQL — only system Python
3.9 with pip/venv. That's why this is Django templates + htmx + SQLite instead
of React + Postgres (an explicitly allowed Phase 1 fallback per the spec).
If you install Node/Postgres later, Phase 3's React/Postgres migration is still
open. There's also no JS runtime on this machine, so the `dataviz` skill's
`validate_palette.js` couldn't be run directly for the Charts page — it uses
the skill's documented, pre-validated dark-mode palette unmodified instead.
