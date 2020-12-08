from django import forms
from home.forms import UserMultipleWidget
from home.models import User


class ThemeStaffForm(forms.Form):
    staff_list = forms.ModelMultipleChoiceField(
        label='統一テーマ案投票スタッフ',
        queryset=User.objects.staff_list(),
        widget=UserMultipleWidget
    )
