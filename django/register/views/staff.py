from django.contrib import messages
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from penguin import mixins
from project.models import Kind
from register.forms import RegistrationForm, WindowForm
from register.models import Registration, Window


class MenuView(mixins.StaffOnlyMixin, generic.TemplateView):
    """機能一覧
    """
    template_name = 'register/staff_menu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # ログインしているユーザーが担当している Window のインスタンスが存在
        # →窓口業務画面に遷移
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
        # すでに窓口を開けていた場合は、その窓口ページに遷移
        if Window.objects.filter(staff=request.user):
            window = Window.objects.get(staff=request.user)
            if window.registration:
                # 対応中の企画が存在する場合
                return redirect(
                    'register:staff_window_update',
                    window_pk=str(window.id),
                    pk=window.registration.id
                )
            else:
                # 対応中の企画が存在しない場合
                return redirect(
                    'register:staff_window', window_pk=str(window.id)
                )
        return super().get(request, **kwargs)

    def form_valid(self, form):
        # 1 ユーザーにつき登録できる窓口は 1 件まで
        if Window.objects.filter(staff=self.request.user).exists():
            messages.error(
                self.request,
                '1 スタッフが担当できる窓口は 1 件までです！'
                '既に開いている窓口業務画面を閉じてください。'
            )
            return redirect('register:staff_window_open')

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
        # 担当スタッフ以外の閲覧を阻止
        if request.user != self.window.staff:
            raise HttpResponseForbidden
        if self.window.registration:
            # 対応中の企画が存在する場合
            return redirect(
                'register:staff_window_update',
                window_pk=str(self.window.id),
                pk=self.window.registration.id
            )
        return super().get(request, **kwargs)

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
        # 担当スタッフ以外の閲覧を阻止
        if request.user != self.window.staff:
            raise HttpResponseForbidden
        # ステータス更新
        self.registration.call(kwargs['window_pk'])
        return super().get(request, **kwargs)

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
