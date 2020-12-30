import uuid

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from penguin import mixins
from register import forms
from register.models import Registration, VerifiedUser, VerifyToken


class VerifyView(generic.TemplateView):
    template_name = 'register/verify.html'

    def get(self, request, **kwargs):
        # 企画登録トークン確認
        try:
            token_ok = VerifyToken.objects.filter(
                id=uuid.UUID(kwargs['token'])
            ).exists()
        except ValueError:
            # そもそも UUID の形式を満たしていない場合
            raise Http404
        if token_ok:
            # 企画登録トークン正解→企画登録可能ユーザー登録
            VerifiedUser.objects.get_or_create(user=request.user)
        else:
            # UUID の形式は満たしているがトークン不正解
            raise Http404

        return super().get(request, **kwargs)


class CreateView(mixins.RedirectIfNotIdentified, generic.FormView):
    template_name = 'register/create.html'
    model = Registration
    form_class = forms.RegistrationForm
    success_url = reverse_lazy('register:success')

    def get(self, request, **kwargs):
        if not self.check_valid_user(request.user):
            # 企画登録可能ユーザーでない場合
            messages.error('不正なページ遷移です！')
            return redirect('home:index')
        return super().get(request, **kwargs)

    def form_valid(self, form):
        if not self.check_valid_user(self.request.user):
            # 企画登録可能ユーザーでない場合
            messages.error('不正なページ遷移です！')
            return redirect('home:index')
        else:
            # 企画登録可能ユーザーの場合は、企画登録可能ユーザーの情報を削除
            # （1 回の QR コード読み込みで登録できる企画は高々 1 件）
            VerifiedUser.objects.get(user=self.request.user).delete()
        return super().form_valid(form)

    def check_valid_user(self, user):
        """企画登録可能ユーザーかどうかを判定する
        """
        return VerifiedUser.objects.filter(user=user).exists()
