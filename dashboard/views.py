from datetime import date, timedelta
from decimal import Decimal

from django.views.generic import TemplateView

from licences.models import Licence
from shifts.models import Shift


class DashboardView(TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        month_start = today.replace(day=1)

        week_shifts = list(
            Shift.objects.select_related("site", "site__agency")
            .filter(date__gte=week_start, date__lte=week_end)
        )
        month_shifts = Shift.objects.filter(date__gte=month_start, date__lte=today)

        month_total = sum((s.calculated_pay for s in month_shifts), Decimal("0.00"))
        week_total = sum((s.calculated_pay for s in week_shifts), Decimal("0.00"))

        licences = list(Licence.objects.all())
        upcoming_expiries = sorted(
            (l for l in licences if l.is_expired or l.days_until_expiry <= 30),
            key=lambda l: l.days_until_expiry,
        )

        context.update(
            {
                "week_start": week_start,
                "week_end": week_end,
                "week_shifts": week_shifts,
                "week_total": week_total,
                "month_total": month_total,
                "upcoming_expiries": upcoming_expiries,
            }
        )
        return context
