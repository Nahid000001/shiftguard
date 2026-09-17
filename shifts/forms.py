from django import forms

from .models import Shift


class SiteSelect(forms.Select):
    """Embeds each site's default_hourly_rate so the form can auto-fill the
    rate field via JS without a round trip - see shift_form.html."""

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        site_id = value.value if hasattr(value, "value") else value
        if site_id:
            if not hasattr(self, "_rate_by_site_id"):
                self._rate_by_site_id = dict(
                    self.choices.queryset.values_list("pk", "default_hourly_rate")
                )
            rate = self._rate_by_site_id.get(int(site_id)) if str(site_id).isdigit() else None
            if rate is not None:
                option["attrs"]["data-rate"] = str(rate)
        return option


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ["site", "date", "start_time", "end_time", "hourly_rate", "shift_type", "notes"]
        widgets = {
            "site": SiteSelect(),
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "start_time": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "end_time": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
