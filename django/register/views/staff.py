from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from penguin import mixins
from project.models import Kind
from register.forms import RegistrationForm, WindowForm
from register.models import Registration, Window


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
    """企画登録会 窓口業務

    登録企画を選択→呼出・保留・受理・却下が可能
    """
    template_name = 'register/staff_window.html'

    def get(self, request, **kwargs):
        # スタッフが担当している窓口の状況に応じ、必要ならリダイレクト
        redirect = get_redirect(request.user, 'staff_window')
        return redirect if redirect else super().get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Window のインスタンス
        context['window'] = self.window
        context['window_id'] = {'window-id': self.window.id}
        return context

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Window のインスタンスを method で使えるようにする
        self.window = Window.objects.get(id=self.kwargs['window_pk'])


class WindowUpdateView(mixins.StaffOnlyMixin, generic.UpdateView):
    """企画登録会 窓口業務

    登録企画を選択→呼出・保留・受理・却下が可能
    """
    template_name = 'register/staff_window_update.html'
    model = Registration
    form_class = RegistrationForm
    success_url = reverse_lazy('register:staff_window_open')

    def get(self, request, **kwargs):
        # ステータス更新
        self.registration.call(kwargs['window_pk'])
        return super().get(request, **kwargs)
        # スタッフが担当している窓口の状況に応じ、必要ならリダイレクト
        redirect = get_redirect(request.user, 'staff_window_update')
        return redirect if redirect else super().get(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Window のインスタンス
        context['window'] = self.window
        context['window_id'] = {'window-id': self.window.id}
        context['food_list'] = [{
            'kind_id': kind.id,
            'food': kind.food
        } for kind in Kind.objects.all()]
        return context

    def form_valid(self, form):
        # 先回りで保存
        self.object = form.save()

        # 状態更新
        if 'btn_refuse' in form.data:
            self.object.refuse(self.request.user)
            messages.error(self.request, '却下しました！')
        elif 'btn_suspend' in form.data:
            messages.info(self.request, '保留しました！')
            self.object.suspend()
        elif 'btn_accept' in form.data:
            messages.success(self.request, '受理しました！')
            self.object.accept(self.request.user)

        return super().form_valid(form)

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Window のインスタンスを method で使えるようにする
        self.registration = Registration.objects.get(id=self.kwargs['pk'])
        self.window = Window.objects.get(id=self.kwargs['window_pk'])


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


class AdminProcessingView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録会 監督業務

    現在進行中（待機・対応中・保留）の企画登録について表示
    """
    template_name = 'register/staff_admin_processing.html'


class AdminFinishedView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録情報管理

    終了済（受理・却下）の企画登録について表示
    """
    template_name = 'register/staff_admin_finished.html'


class AdminStaffView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録担当スタッフを選択する

    企画登録会 監督業務や企画登録情報管理にアクセスできるスタッフを決定する
    """
    template_name = 'register/staff_admin_staff.html'


class AdminSlackView(mixins.StaffOnlyMixin, generic.TemplateView):
    """企画登録 slack ch. を指定する
    """
    template_name = 'register/staff_admin_slack.html'
