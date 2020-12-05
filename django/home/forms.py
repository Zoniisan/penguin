from django import forms
from django.contrib.auth import authenticate
from django_select2 import forms as s2forms

from home.models import (Contact, ContactKind, Department, IdentifyToken,
                         Message, Notice, User)


class UserMultipleWidget(s2forms.ModelSelect2MultipleWidget):
    search_fields = [
        "stid__icontains",
        "last_name__icontains",
        "first_name__icontains",
        "last_name_kana__icontains",
        "first_name_kana__icontains",
    ]


class LoginForm(forms.Form):
    eptid = forms.CharField(
        label='EPTID',
        max_length=200,
    )

    def clean_eptid(self):
        eptid = self.cleaned_data['eptid']
        user = authenticate(eptid=eptid)
        if user:
            return eptid
        else:
            raise forms.ValidationError('この eptid は利用できません。')


class IdentifyTokenForm(forms.ModelForm):
    class Meta:
        model = IdentifyToken
        fields = (
            'email',
        )

    def clean_email(self):
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            # 既にそのメールアドレスが使用されている場合
            raise forms.ValidationError('このメールアドレスは既に使用されています')
        else:
            return self.cleaned_data['email']


class IdentifyForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'stid', 'tel', 'last_name', 'first_name',
            'last_name_kana', 'first_name_kana',
            'faculty', 'grade'
        )


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = (
            'subject', 'body', 'start_datetime', 'finish_datetime'
        )


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = (
            'name', 'email', 'slack_ch', 'member'
        )
        widgets = {
            "member": UserMultipleWidget,
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            'stid', 'email', 'tel', 'last_name', 'first_name',
            'last_name_kana', 'first_name_kana',
            'faculty', 'grade', 'is_active', 'is_admin',
            'affiliation'
        )


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = (
            'to', 'subject', 'body', 'department'
        )
        widgets = {
            'to': UserMultipleWidget,
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = (
            'kind', 'body'
        )


class ContactKindForm(forms.ModelForm):
    class Meta:
        model = ContactKind
        fields = (
            'name', 'slack_ch', 'department'
        )
        widgets = {
            'department': forms.CheckboxSelectMultiple
        }
