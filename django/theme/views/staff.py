from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from theme.forms import ThemeSlackForm, ThemeStaffForm
from theme.models import (SubmitSchedule, Theme, ThemeSlack, ThemeStaff,
                          VoteSchedule)


class ThemeStaffOnlyMixin(UserPassesTestMixin):
    """統一テーマ担当スタッフ専用

    該当するページはこれを継承すること
    """
    raise_exception = True

    def test_func(self):
        return (
            self.request.user.is_authenticated and
            ThemeStaff.objects.check_perm(self.request.user)
        )


class MenuView(ThemeStaffOnlyMixin, generic.TemplateView):
    """統一テーマ担当スタッフメニュー

    統一テーマ案投票管理
    統一テーマ案投票担当スタッフ一覧
    slack ch.
    へのインターフェースを提供
    """
    template_name = 'theme/staff_menu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 統一テーマ案投票管理
        # 提出日程
        context["submit_schedule"] = SubmitSchedule.objects.filter().first()
        # 提出日程が有効なら True
        context["submit_schedule_is_active"] = \
            SubmitSchedule.objects.is_active()
        # 統一テーマ案提出件数
        context['theme_count'] = Theme.objects.all().count()
        # 投票日程一覧
        context['vote_schedule_list'] = VoteSchedule.objects.all().order_by(
            'start_datetime'
        )

        # 統一テーマ案投票担当スタッフ一覧
        context["theme_staff_list"] = ThemeStaff.objects.get_user_list()

        # slack ch.
        slack = ThemeSlack.objects.all().first()
        if slack:
            context["verbose_slack_ch"] = slack.verbose_slack_ch()

        return context


class ThemeStaffView(ThemeStaffOnlyMixin, generic.FormView):
    """統一テーマ案投票担当スタッフ管理

    統一テーマ案投票担当スタッフを選択
    """
    template_name = 'theme/staff_theme_staff.html'
    form_class = ThemeStaffForm
    success_url = reverse_lazy('theme:staff_menu')

    def get_form(self):
        form = super().get_form()

        # 初期値として現在の統一テーマ案投票担当スタッフをセット
        form.fields['staff_list'].initial = ThemeStaff.objects.get_user_list()

        return form

    def form_valid(self, form):
        with transaction.atomic():
            # 現在の統一テーマ案投票担当スタッフの権限を
            # 一時的に全員解除
            ThemeStaff.objects.all().delete()

            # フォームに入力されたスタッフに対し、
            # 統一テーマ案投票担当スタッフの権限を付与
            for user in form.cleaned_data['staff_list']:
                ThemeStaff.objects.create(user=user)

        messages.success(
            self.request, '統一テーマ案投票担当スタッフを登録しました！'
        )

        return super().form_valid(form)


class ThemeSlackView(ThemeStaffOnlyMixin, generic.CreateView):
    """統一テーマ関連 slack ch. を設定

    設定すると統一テーマ案提出時に通知される
    設定しない場合は slack が送信されない
    """
    template_name = 'theme/staff_theme_slack.html'
    model = ThemeSlack
    form_class = ThemeSlackForm
    success_url = reverse_lazy('theme:staff_menu')

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # 現時点での ThemeSlack があれば取得（なければ None）
        self.asis_theme_slack = ThemeSlack.objects.all().first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["asis_theme_slack"] = self.asis_theme_slack
        return context

    def get_form(self):
        form = super().get_form()

        # 現時点で ThemeSlack のインスタンスがある場合は、
        # その値をフォーム初期値として登録
        if self.asis_theme_slack:
            form.fields['slack_ch'].initial = self.asis_theme_slack.slack_ch

        return form

    def form_valid(self, form):
        messages.success(self.request, 'slack ch. を登録しました！')
        return super().form_valid(form)


class ThemeSlackDeleteView(ThemeStaffOnlyMixin, generic.RedirectView):
    """統一テーマ関連 slack ch. を削除
    """
    pattern_name = 'theme:staff_menu'

    def get_redirect_url(self, *args, **kwargs):
        # 削除
        obj = get_object_or_404(ThemeSlack)
        obj.delete()

        messages.error(self.request, 'slack ch. を削除しました！')

        # args / kwargs は捨てる
        return super().get_redirect_url()
