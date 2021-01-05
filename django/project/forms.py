from django import forms
from home.forms import StaffMultipleWidget

from project.models import Kind


class KindForm(forms.ModelForm):
    class Meta:
        model = Kind
        fields = (
            'name', 'symbol', 'food', 'slack_ch', 'staff_list'
        )
        widgets = {
            'staff_list': StaffMultipleWidget
        }
