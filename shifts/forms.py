from django import forms

from .models import Shift


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ["site", "date", "start_time", "end_time", "hourly_rate", "shift_type", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "start_time": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "end_time": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }
