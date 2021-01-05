from django import forms
from home.forms import UserMultipleWidget
from home.models import User

from register import models


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = models.Registration
        fields = (
            'kind', 'food', 'group', 'group_kana', 'note'
        )


class WindowForm(forms.ModelForm):
    class Meta:
        model = models.Window
        fields = (
            'name', 'kind_list'
        )
        widgets = {
            'kind_list': forms.CheckboxSelectMultiple
        }


class RegistrationStaffForm(forms.Form):
    staff_list = forms.ModelMultipleChoiceField(
        label='企画登録管理スタッフ',
        queryset=User.objects.staff_list(),
        widget=UserMultipleWidget,
        required=False
    )
