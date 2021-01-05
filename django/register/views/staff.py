from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic
from home.tasks import send_mail_async
from penguin import mixins
from project.models import Kind
from register.forms import RegistrationForm, RegistrationStaffForm, WindowForm
from register.models import RegisterStaff, Registration, Window
from register.serializer import RegistrationSerializer
from rest_framework import permissions, viewsets


def get_redirect(staff, origin):
    """スタッフが担当している窓口の状況に応じ、必要ならリダイレクト

    Args:
        staff(User): スタッフ
        origin(str): リダイレクト元の path
    Returns:
        HttpRequest: リダイレクト先（必要ないなら None）
    """
    # スタッフが担当している窓口があれば取得
    window = Window.objects.filter(staff=staff).first()

    if window:
        if window.registration:
            # 窓口を開設していて、対応中の企画が存在する
            # →窓口対応画面へ
            if origin != 'staff_window_update':
                return redirect(
                    'register:staff_window_update',
                    window_pk=window.id,
                    pk=window.registration.id
                )
        else:
            # 窓口を開設しているが、対応中の企画は存在しない
            # →窓口待機画面へ
            if origin != 'staff_window':
                return redirect(
                    'register:staff_window',
                    window_pk=window.id
                )
    else:
        # 窓口を開設していない
        # →窓口開設画面へ
        if origin != 'staff_window_open':
            return redirect('register:staff_window_open')


class MenuView(mixins.StaffOnlyMixin, generic.TemplateView):
    """機能一覧

    スタッフが行う企画登録業務の一覧を表示
    """
    template_name = 'register/staff_menu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ログインしているユーザーが担当している Window のインスタンスが存在
        # →機能一覧画面に窓口名を表示
        if Window.objects.filter(staff=self.request.user).exists():
            context['window'] = Window.objects.get(staff=self.request.user)
        # 企画登録管理スタッフであれば、専用メニューを表示
        context['is_register_staff'] = \
            RegisterStaff.objects.check_perm(self.request.user)
        return context


class WindowOpenView(mixins.StaffOnlyMixin, generic.CreateView):
    """企画登録会 窓口業務 開始

    窓口名と対応する企画種別を選択
    """
    template_name = 'register/staff_window_open.html'
    model = Window
    form_class = WindowForm

    def get(self, request, **kwargs):
        # スタッフが担当している窓口の状況に応じ、必要ならリダイレクト
        redirect = get_redirect(request.user, 'staff_window_open')
        return redirect if redirect else super().get(request, **kwargs)

    def form_valid(self, form):
        # 担当 staff 登録
        form.instance.staff = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'register:staff_window', kwargs={'window_pk': self.object.pk}
        )


class WindowView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録会 窓口業務 待機状態

    待機中・保留中の企画から呼び出したい企画を選択する
    """
    template_name = 'register/staff_window.html'

    def get(self, request, **kwargs):
        # スタッフが担当している窓口の状況に応じ、必要ならリダイレクト
        redirect = get_redirect(request.user, 'staff_window')
        return redirect if redirect else super().get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Window のインスタンスを URL に応じて取得
        window = Window.objects.get(id=self.kwargs['window_pk'])
        # template 描画用
        context['window'] = window
        # 窓口の情報
        context['window_data'] = {
            'id': window.id,
            'kind_id_list': [str(kind.id) for kind in window.kind_list.all()],
        }

        return context


class WindowUpdateView(mixins.StaffOnlyMixin, generic.UpdateView):
    """企画登録会 窓口業務

    登録企画を選択→呼出・保留・受理・却下が可能
    """
    template_name = 'register/staff_window_update.html'
    model = Registration
    form_class = RegistrationForm
    success_url = reverse_lazy('register:staff_window_open')

    def get(self, request, **kwargs):
        # 該当企画の状態を「対応中」に更新
        self.registration.call(kwargs['window_pk'])
        # スタッフが担当している窓口の状況に応じ、必要ならリダイレクト
        redirect = get_redirect(request.user, 'staff_window_update')
        return redirect if redirect else super().get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Window のインスタンス（template 描画用）
        context['window'] = self.window
        # Window のインスタンス（websocket 送信用）
        context['window_data'] = {'id': self.window.id}
        # 企画種別ごとの飲食物提供情報を取得
        context['food_list'] = [{
            'kind_id': kind.id,
            'food': kind.food
        } for kind in Kind.objects.all()]

        return context

    def form_valid(self, form):
        # 先回りで保存して登録コードを付与
        self.object = form.save()

        # 押されたボタンに応じ、該当企画の状態を更新
        if 'btn_refuse' in form.data:
            self.object.refuse(self.request.user)
            messages.error(self.request, '却下しました！')
        elif 'btn_suspend' in form.data:
            messages.info(self.request, '保留しました！')
            self.object.suspend()
        elif 'btn_accept' in form.data:
            messages.success(self.request, '受理しました！')
            self.send_mail(self.object)
            self.object.accept(self.request.user)

        return super().form_valid(form)

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # インスタンスを method で使えるようにする
        self.registration = Registration.objects.get(id=self.kwargs['pk'])
        self.window = Window.objects.get(id=self.kwargs['window_pk'])

    def send_mail(self, registration):
        """メールを送信する

        Args:
            registration(Registration): Registration のインスタンス
        Returns:
            None
        """
        # メッセージ本文を作成
        message = render_to_string(
            'register/mail/accept.html',
            {
                'registration': registration,
                'BASE_URL': settings.BASE_URL,
            }
        )

        # メール送信
        send_mail_async(
            'PENGUIN ユーザー登録はまだ完了していません',
            [{'recipient': registration.temp_leader.email, 'message': message}]
        )


class WindowCloseView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録会 窓口業務 終了
    """
    template_name = 'register/staff_window_close.html'

    def get(self, request, **kwargs):
        # Window インスタンスを削除
        obj = get_object_or_404(Window, id=kwargs['pk'])
        obj.delete()
        return super().get(request, **kwargs)


class SignageView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録会 案内表示

    企画登録 QR コードと各窓口の対応状況を表示
    """
    template_name = 'register/staff_signage.html'


# これ以降は企画登録管理スタッフ専用ページ

class RegisterStaffOnlyMixin(UserPassesTestMixin):
    """企画登録管理スタッフ専用

    企画登録管理スタッフ専用ページの View クラスはこれを継承すること
    """
    raise_exception = True

    def test_func(self):
        return RegisterStaff.objects.check_perm(self.request.user)


class AdminListView(RegisterStaffOnlyMixin, generic.TemplateView):
    """登録完了企画一覧

    企画登録（受理）について表示
    """
    template_name = 'register/staff_admin_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 企画種別一覧
        context['kind_list'] = Kind.objects.all()

        return context


class RegistrationPermission(permissions.BasePermission):
    """[REST framework] システム管理者専用

    企画登録管理スタッフ以外アクセスできない ViewSet はこれを利用すること
    """
    message = '企画登録管理スタッフ以外アクセスできません。'

    def has_permission(self, request, view):
        return RegisterStaff.objects.check_perm(request.user)


class RegistrationViewSet(viewsets.ModelViewSet):
    """[ViewSet] Registration

    AdminListView で使用
    """
    queryset = Registration.objects.filter(status='accepted')
    serializer_class = RegistrationSerializer

    # 企画登録管理スタッフ以外アクセス禁止
    permission_classes = (RegistrationPermission,)


class AdminDetailView(RegisterStaffOnlyMixin, generic.DetailView):
    """登録企画情報の詳細を閲覧
    """
    template_name = 'register/staff_admin_detail.html'
    model = Registration


class AdminLiveView(RegisterStaffOnlyMixin, generic.TemplateView):
    """企画登録会 監督業務
    """
    template_name = 'register/staff_admin_live.html'


class AdminStaffView(RegisterStaffOnlyMixin, generic.FormView):
    """統一テーマ案投票担当スタッフ管理

    統一テーマ案投票担当スタッフを選択
    """
    template_name = 'register/staff_admin_staff.html'
    form_class = RegistrationStaffForm
    success_url = reverse_lazy('register:staff_admin_staff')

    def get_form(self):
        form = super().get_form()

        # 初期値として現在の統一テーマ案投票担当スタッフをセット
        form.fields['staff_list'].initial = \
            RegisterStaff.objects.get_user_list()

        return form

    def form_valid(self, form):
        with transaction.atomic():
            # 現在の統一テーマ案投票担当スタッフの権限を
            # 一時的に全員解除
            RegisterStaff.objects.all().delete()

            # フォームに入力されたスタッフに対し、
            # 統一テーマ案投票担当スタッフの権限を付与
            for user in form.cleaned_data['staff_list']:
                RegisterStaff.objects.create(user=user)

        messages.success(
            self.request, '企画登録管理スタッフを登録しました！'
        )

        return super().form_valid(form)
