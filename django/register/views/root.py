import uuid

from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from penguin import mixins
from project.models import Kind
from register import forms
from register.models import Registration, VerifiedUser, VerifyToken


class VerifyView(generic.TemplateView):
    """企画登録 QR コードの真正性をチェック

    企画登録したいユーザーは、企画登録会会場に表示される QR コードを読み込む。
    QR コードの内容が正しければ、そのユーザーを含む VerifiedUser の
    インスタンスが作成され、企画登録が可能となる。
    """
    template_name = 'register/root_verify.html'

    def get(self, request, **kwargs):
        # アクセスされた URL と、企画登録 QR コードの内容が
        # 一致するかどうかを確認する
        try:
            if VerifyToken.objects.filter(
                id=uuid.UUID(kwargs['token'])
            ).exists():
                # 一致した場合は VerifiedUser のインスタンスを作成
                VerifiedUser.objects.create(user=request.user)
            else:
                # そうでなければ 404 を返す
                raise Http404
        except ValueError:
            # そもそも UUID の形式を満たしていない場合も 404 を返す
            raise Http404

        return super().get(request, **kwargs)


class CreateView(mixins.RedirectIfNotIdentified, generic.FormView):
    """企画登録フォーム

    ユーザーが登録したい企画の内容を入力する。
    """
    template_name = 'register/root_create.html'
    model = Registration
    form_class = forms.RegistrationForm

    def get(self, request, **kwargs):
        # 企画登録可能ユーザーでない場合→アクセス不可
        if not VerifiedUser.objects.check_user(request.user):
            messages.error(request, '不正なページ遷移です！')
            return redirect('home:index')
        return super().get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 企画種別ごとの飲食物提供情報を取得
        context['food_list'] = [{
            'kind_id': kind.id,
            'food': kind.food
        } for kind in Kind.objects.all()]

        return context

    def form_valid(self, form):
        if VerifiedUser.objects.check_user(self.request.user):
            with transaction.atomic():
                # 企画登録可能ユーザーの場合は、企画登録可能ユーザーの情報を削除
                # （1 回の QR コード読み込みで登録できる企画は高々 1 件）
                VerifiedUser.objects.get(user=self.request.user).delete()
                # 仮企画責任者登録
                form.instance.temp_leader = self.request.user
                # 企画登録情報を保存
                self.object = form.save()
            # 整理番号を発行
            self.object.set_call_id()
        else:
            # 企画登録可能ユーザーでない場合→フォーム送信不可
            messages.error(self.request, '不正なページ遷移です！')
            return redirect('home:index')

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'register:success', kwargs={'pk': self.object.pk}
        )


class SuccessView(mixins.IdentifiedOnlyMixin, generic.DetailView):
    """企画登録フォーム 入力完了

    整理番号を表示する
    """
    template_name = 'register/root_success.html'
    model = Registration
