from django import forms

from .models import Licence


class LicenceForm(forms.ModelForm):
    class Meta:
        model = Licence
        fields = ["name", "licence_number", "issue_date", "expiry_date", "reminder_days_before"]
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "expiry_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }
