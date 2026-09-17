# Multi-Agency Security Shift & Pay Tracker

## 1. Project Overview

**Name (working title):** ShiftGuard (rename freely)

**One-line pitch:** A web app for security contractors working across multiple agencies to track shifts, pay, licence expiries, and self-employment income in one place.

**Who it's for:** Security officers/contractors juggling multiple employers (PAYE + self-employed), especially those holding SIA licences that must stay valid, and who need clean records for tax self-assessment.

**Why it exists (problems it solves):**

- Shifts are scattered across multiple agencies with no single view of the week/month.
- Pay varies by agency/site/shift type — easy to be underpaid without noticing.
- SIA licence expiry is a hard legal deadline; missing it means you can't legally work.
- Sole traders need clean hours/income records for invoicing and HMRC self-assessment.
- No single view of total earnings across PAYE + self-employed income streams.

**Not in scope for v1:** automatic pulling of rota data from third-party employer systems (no public API access as an individual contractor) — see Section 6 for the realistic alternative.

## 2. Users

Single-user app for v1 (just you). Multi-user/auth comes in Phase 3 if this becomes a real product.

## 3. Core Data Model

### Agency
- id
- name (e.g. "Mitie", "Securitas", "R5 Global")
- employment_type: enum [PAYE, SELF_EMPLOYED]
- contact_notes (optional)

### Site
- id
- agency_id (FK -> Agency)
- name (e.g. "BNY Mellon Blackfriars")
- address (optional)
- default_hourly_rate (optional, decimal)

### Shift
- id
- site_id (FK -> Site)
- date
- start_time
- end_time
- hourly_rate (decimal — can override site default)
- calculated_pay (derived: hours * rate, store or compute on read)
- shift_type: enum [STANDARD, OVERTIME, NIGHT, BANK_HOLIDAY] (optional, for rate variation)
- notes (optional)

### Licence
- id
- name (e.g. "SIA Door Supervisor", "SIA CCTV")
- licence_number
- issue_date
- expiry_date
- reminder_days_before (default: 60)

### Expense (Phase 2)
- id
- date
- category: enum [UNIFORM, TRAVEL, EQUIPMENT, OTHER]
- amount
- agency_id (nullable FK — link to self-employed work if relevant)
- notes

### TaxPeriod (Phase 2, derived/reporting only — not necessarily its own table)
- Aggregates Shift + Expense by UK tax quarter for export

## 4. Build Phases

### Phase 1 — MVP (core tracker)
- CRUD for Agency, Site, Shift, Licence
- Dashboard view: this week's shifts, this month's earnings total, upcoming licence expiries (highlighted if <30 days)
- Shift entry form with a "duplicate last shift" quick-add option
- Basic pay calculation (hours × rate) per shift, summed weekly/monthly

**Definition of done:** you can log a week of real shifts across your actual agencies and see accurate totals and licence status at a glance.

### Phase 2 — Sole trader layer
- Tag shifts by employment_type via their Agency (already in data model)
- Expense logging (CRUD)
- Export: CSV or PDF summary grouped by UK tax quarter (6 Apr–5 Jul, etc.), split PAYE vs self-employed
- Simple year-to-date self-employed income total (for self-assessment prep)

### Phase 3 — Polish / portfolio-readiness
- Auth (so it's demoable as a real product, not just local-only)
- Charts: earnings trend over time, hours by agency, pay by site
- Mobile-friendly (PWA or just solid responsive design) — you'll realistically use this on your phone between shifts
- Optional: email parsing for shift confirmations (see Section 6)

## 5. Tech Stack

- **Backend:** Django + Django REST Framework
- **Frontend:** React (Phase 1 can use Django templates + HTMX if you want to ship faster, then migrate to React in Phase 3)
- **Database:** PostgreSQL
- **Auth (Phase 3):** Django's built-in auth + DRF token/session auth
- **Deployment:** Vercel (frontend) + Azure or Railway/Render (backend + Postgres) — Azure gives you a resume-relevant line given your existing exposure
- **Task scheduling (licence alerts, Phase 3):** Celery + Redis, or a simple cron-triggered management command if you want to avoid the extra infra
- **Charts:** Recharts (React) or Chart.js

## 6. On Automation (set expectations correctly)

Full automatic sync from Mitie/Securitas/R5's internal rota systems is not realistically achievable for v1 — you won't have API access as an individual contractor, and scraping is fragile and may violate platform terms. Realistic options, in order of effort:

1. **Manual entry optimized for speed (v1 default)** — quick-add, "duplicate last shift," templates for recurring patterns.
2. **Email parsing (Phase 3 stretch)** — if any agency sends shift confirmation emails, a Gmail API integration can auto-extract shift data from a consistent email format.
3. **OCR import (Phase 3 stretch)** — if rotas arrive as PDF/image, extract shift data via OCR instead of typing.
4. **True API integration** — only if you confirm Mitie/Securitas/R5 use a known platform (e.g. RotaCloud, Deputy — both have APIs) and you can get contractor-level read access. Worth asking, costs nothing.

## 7. How to Use This With Cursor + Claude Code CLI

Suggested approach once you open this repo in Cursor:

1. Start with `claude` in the project root and paste this spec as context, or reference this file directly (`Read shift-tracker-project-spec.md and scaffold the Django project structure per Phase 1`).
2. Build Phase 1 end-to-end before touching Phase 2 — resist scope creep.
3. Ask Claude Code to scaffold in this order: Django project + apps → models + migrations → DRF serializers/viewsets → basic React frontend hitting the API → dashboard view last.
4. Commit after each working slice (models working, API working, frontend working) so you have clean rollback points.

## 8. Success Criteria for v1

- You personally use it for at least 2-4 weeks of real shifts instead of your current method (whatever that is now — notes app, memory, etc.)
- Weekly/monthly pay totals match what you're actually paid
- Licence expiry is visible without you having to remember to check
