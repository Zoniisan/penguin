from django import forms
from home.forms import UserMultipleWidget, UserWidget
from home.models import User

from theme import models


class ThemeForm(forms.ModelForm):
    class Meta:
        model = models.Theme
        fields = (
            'theme', 'description'
        )


class StaffSubmitForm(forms.ModelForm):
    class Meta:
        model = models.Theme
        fields = (
            'theme', 'description', 'writer'
        )
        widgets = {
            'writer': UserWidget
        }

    def clean_writer(self):
        writer = self.cleaned_data['writer']

        # 提出済みのユーザーであれば拒否
        if models.Theme.objects.can_submit_check(writer):
            return writer
        else:
            raise forms.ValidationError('このユーザーは既に提出済みです。')


class ThemeStaffForm(forms.Form):
    staff_list = forms.ModelMultipleChoiceField(
        label='統一テーマ案投票スタッフ',
        queryset=User.objects.staff_list(),
        widget=UserMultipleWidget
    )


class SubmitScheduleForm(forms.ModelForm):
    class Meta:
        model = models.SubmitSchedule
        fields = (
            'start_datetime', 'finish_datetime'
        )


class ThemeSlackForm(forms.ModelForm):
    class Meta:
        model = models.ThemeSlack
        fields = (
            'slack_ch',
        )


class VoteScheduleForm(forms.ModelForm):
    class Meta:
        model = models.VoteSchedule
        fields = (
            'name', 'description', 'start_datetime', 'finish_datetime'
        )


class NoneForm(forms.Form):
    pass
