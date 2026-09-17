from django import forms

from .models import Agency, Site


class AgencyForm(forms.ModelForm):
    class Meta:
        model = Agency
        fields = ["name", "employment_type", "contact_notes"]
        widgets = {"contact_notes": forms.Textarea(attrs={"rows": 3})}


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = ["agency", "name", "address", "default_hourly_rate"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["agency"].queryset = Agency.objects.filter(user=user)
