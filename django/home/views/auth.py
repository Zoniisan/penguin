import datetime

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic
from home.forms import IdentifyForm, IdentifyTokenForm, LoginForm, UserForm
from home.models import IdentifyToken, User
from home.serializer import UserSerializer
from home.tasks import send_mail_async
from penguin import mixins
from penguin.auth import IsAdminPermission
from rest_framework import viewsets


class ProfileView(generic.TemplateView):
    """プロフィール

    ログインしているユーザーの情報を表示
    """
    template_name = 'home/auth_profile.html'


class IdentifyTokenCreateView(
    mixins.NotIdentifiedOnlyMixin, generic.CreateView
):
    """メールアドレス入力

    メールアドレスを入力すると、個人情報入力を行うための
    URL が添付されたメールが送信される。
    """
    template_name = 'home/auth_identify_token_create.html'
    model = IdentifyToken
    form_class = IdentifyTokenForm
    success_url = reverse_lazy('home:auth_identify_token_success')

    def form_valid(self, form):
        # IdentifyToken に request.user の EPTID を登録
        form.instance.eptid = self.request.user.eptid

        # 先回りで保存して IdentifyToken の id を発行
        self.object = form.save()

        # IdentifyToken を入力されたメールアドレス宛に送信
        self.send_mail(self.object)

        return super().form_valid(form)

    def send_mail(self, token):
        """メールを送信する

        Args:
            message(Message): Message のインスタンス
        Returns:
            None
        """
        # メッセージ本文を作成
        message = render_to_string(
            'home/mail/identify_token.html',
            {
                'token': token,
                'BASE_URL': settings.BASE_URL
            }
        )

        # メール送信
        send_mail_async(
            'PENGUIN ユーザー登録はまだ完了していません',
            [{'recipient': token.email, 'message': message}]
        )


class IdentifyTokenSuccessView(
    mixins.NotIdentifiedOnlyMixin, generic.TemplateView
):
    """メールアドレス入力完了

    ユーザーにメールの確認を促す。
    """
    template_name = 'home/auth_identify_token_success.html'


class IdentifyView(generic.UpdateView):
    """個人情報入力

    IdentifyTokenView によって送信されたメールに記載された URL にアクセス
    することでこの View にアクセスできる。
    """
    template_name = 'home/auth_identify.html'
    form_class = IdentifyForm
    success_url = reverse_lazy('home:index')

    def get(self, request, **kwargs):
        # eptid 不一致
        # メールアドレスを入力したユーザーと
        # URL にアクセスしたユーザーが異なる場合
        if self.token.eptid != request.user.eptid:
            messages.error(
                request,
                'メールアドレスを入力したユーザーと現在ログインしているユーザーが異なります。'
            )
            return redirect('home:index')

        # 有効期限切れ
        limit = datetime.datetime.now() - datetime.timedelta(minutes=30)
        if self.token.create_datetime < limit:
            messages.error(
                request,
                'この URL は期限切れです。もう一度メールアドレスの入力からやり直してください。'
            )
            return redirect('home:auth_identify_token_create')

        # 使用済
        if self.token.is_used:
            messages.error(
                request,
                'この URL は使用済です。もう一度メールアドレスの入力からやり直してください。'
            )
            return redirect('home:auth_identify_token_create')

        # 問題なければ token 使用済とする
        self.token.is_used = True
        self.token.save()

        return super().get(request, **kwargs)

    def form_valid(self, form):
        # email は IdentifyToken の値を取得
        form.instance.email = self.token.email

        # alert
        messages.success(
            self.request, '個人情報の入力が完了しました！'
        )

        return super().form_valid(form)

    def get_object(self):
        # ログインしているユーザーについて情報を更新する
        return self.request.user

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # IdentifyToken を method で使えるようにする
        self.token = IdentifyToken.objects.get(id=self.kwargs['token_id'])


class UserListView(mixins.AdminOnlyMixin, generic.TemplateView):
    """ユーザー一覧

    全 PENGUIN アカウントを表示
    """
    template_name = 'home/auth_user_list.html'


class UserDetailView(mixins.AdminOnlyMixin, generic.DetailView):
    """ユーザー詳細

    任意の PENGUIN アカウントの詳細を表示
    """
    template_name = 'home/auth_user_detail.html'
    model = User


class UserUpdateView(mixins.AdminOnlyMixin, generic.UpdateView):
    """ユーザー更新

    PENGUIN アカウントの情報を更新
    """
    template_name = 'home/auth_user_update.html'
    model = User
    form_class = UserForm

    def get_success_url(self):
        return reverse_lazy(
            'home:auth_user_detail', kwargs={'pk': self.object.pk}
        )

    def form_valid(self, form):
        # alert
        messages.success(self.request, 'ユーザー情報を更新しました！')

        return super().form_valid(form)


class UserDeleteView(mixins.AdminOnlyMixin, generic.RedirectView):
    """ユーザー削除

    PENGUIN アカウントの情報を削除
    shibboleth 認証の場合、削除したあと同じユーザーがログインすると、
    同じ eptid が記録される。BAN する場合は削除ではなく User.is_active = False
    とすること。
    """
    permanent = True
    pattern_name = 'home:auth_user_list'

    def get_redirect_url(self, *args, **kwargs):
        # 削除
        obj = get_object_or_404(User, id=kwargs['pk'])
        obj.delete()

        messages.error(self.request, 'ユーザーを削除しました！')

        # args / kwargs は捨てる
        return super().get_redirect_url()


class LoginView(generic.FormView):
    """ログイン

    local 認証の仕組みは penguin.auth.NoPasswordBackend 参照
    """
    template_name = 'home/auth_login.html'
    form_class = LoginForm
    success_url = reverse_lazy('home:index')

    def form_valid(self, form):
        # authenticate -> login
        user = authenticate(eptid=form.cleaned_data['eptid'])
        login(self.request, user)

        messages.success(
            self.request, 'こんにちは{}さん！ログインしました！'.format(
                self.request.user.get_full_name()
            )
        )

        return super().form_valid(form)


class LogoutView(generic.RedirectView):
    """ログアウト

    local 認証の場合は logout(request) でログアウトできる
    """
    permanent = True
    pattern_name = 'home:index'

    def get_redirect_url(self, *args, **kwargs):
        # local logout
        logout(self.request)
        messages.success(self.request, 'ログアウトしました！')
        return super().get_redirect_url()


class UserViewSet(viewsets.ModelViewSet):
    """[ViewSet] User

    UserListView で使用
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    # システム管理者以外アクセス禁止
    permission_classes = (IsAdminPermission,)
