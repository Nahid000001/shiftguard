from datetime import date, timedelta
from decimal import Decimal

from licences.models import Licence
from shifts.models import Shift


def _add_months(d, months):
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, 1)


def build_dashboard_summary(user):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    month_start = today.replace(day=1)

    week_shifts = list(
        Shift.objects.filter(site__agency__user=user)
        .select_related("site", "site__agency")
        .filter(date__gte=week_start, date__lte=week_end)
    )
    month_shifts = Shift.objects.filter(
        site__agency__user=user, date__gte=month_start, date__lte=today
    )

    month_total = sum((s.calculated_pay for s in month_shifts), Decimal("0.00"))
    week_total = sum((s.calculated_pay for s in week_shifts), Decimal("0.00"))

    licences = list(Licence.objects.filter(user=user))
    upcoming_expiries = sorted(
        (l for l in licences if l.is_expired or l.days_until_expiry <= 30),
        key=lambda l: l.days_until_expiry,
    )

    return {
        "week_start": week_start,
        "week_end": week_end,
        "week_shifts": week_shifts,
        "week_total": week_total,
        "month_total": month_total,
        "upcoming_expiries": upcoming_expiries,
    }


def _bucket_by_category(totals):
    """Cap at 8 categories (chart color-slot limit), folding the smallest into 'Other'.

    Category-to-color assignment must key off a stable order (name), never the
    value ranking, so an entity keeps its color even as amounts change over time.
    """
    stable_order = sorted(totals.keys())
    if len(stable_order) <= 8:
        names = stable_order
    else:
        kept = set(sorted(totals, key=lambda n: -totals[n])[:7])
        other_total = sum(v for n, v in totals.items() if n not in kept)
        totals = {n: v for n, v in totals.items() if n in kept}
        totals["Other"] = other_total
        names = sorted(kept) + ["Other"]

    display_order = sorted(names, key=lambda n: -totals[n])
    return [
        {"name": n, "value": totals[n], "color_index": names.index(n)} for n in display_order
    ]


def build_charts_data(user):
    today = date.today()
    all_shifts = list(
        Shift.objects.filter(site__agency__user=user).select_related("site", "site__agency")
    )

    months = [_add_months(today.replace(day=1), -i) for i in range(5, -1, -1)]
    trend = []
    for i, month_start in enumerate(months):
        month_end = (
            months[i + 1] - timedelta(days=1)
            if i + 1 < len(months)
            else _add_months(month_start, 1) - timedelta(days=1)
        )
        total = sum(
            (s.calculated_pay for s in all_shifts if month_start <= s.date <= month_end),
            Decimal("0.00"),
        )
        trend.append({"label": month_start.strftime("%b %Y"), "total": float(total)})

    hours_by_agency = {}
    for s in all_shifts:
        name = s.site.agency.name
        hours_by_agency[name] = hours_by_agency.get(name, 0) + float(s.duration_hours)

    pay_by_site = {}
    for s in all_shifts:
        name = s.site.name
        pay_by_site[name] = pay_by_site.get(name, 0) + float(s.calculated_pay)

    return {
        "trend": trend,
        "hours_by_agency": _bucket_by_category(hours_by_agency),
        "pay_by_site": _bucket_by_category(pay_by_site),
        "has_data": bool(all_shifts),
    }
