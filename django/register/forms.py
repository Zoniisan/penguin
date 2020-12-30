from django import forms
from register import models


class RegistrationForm(forms.ModelForm):
    class Meta:
        model = models.Registration
        fields = (
            'kind', 'food', 'group', 'group_kana', 'note'
        )
