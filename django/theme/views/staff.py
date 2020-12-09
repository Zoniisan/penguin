from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from theme.forms import ThemeSlackForm, ThemeStaffForm
from theme.models import SubmitSchedule, ThemeSlack, ThemeStaff


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
    template_name = 'theme/staff_menu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 提出期間
        context["submit_schedule"] = SubmitSchedule.objects.filter().first()
        # 提出期間有効
        context["submit_schedule_is_active"] = \
            SubmitSchedule.objects.is_active()
        # 統一テーマ案投票担当スタッフ一覧
        context["theme_staff_list"] = ThemeStaff.objects.all_list()
        # slack ch.
        slack = ThemeSlack.objects.all().first()
        if slack:
            context["verbose_slack_ch"] = slack.verbose_slack_ch()
        return context


class ThemeStaffView(ThemeStaffOnlyMixin, generic.FormView):
    template_name = 'theme/staff_theme_staff.html'
    form_class = ThemeStaffForm
    success_url = reverse_lazy('theme:staff_menu')

    def get_form(self):
        form = super().get_form()

        # 初期値として現在の統一テーマ案投票担当スタッフをセット
        form.fields['staff_list'].initial = ThemeStaff.objects.all_list()

        return form

    def form_valid(self, form):
        # 現在の統一テーマ案投票担当スタッフの権限を一時的に剥奪
        ThemeStaff.objects.all().delete()

        # 統一テーマ案投票担当スタッフの権限を付与
        for user in form.cleaned_data['staff_list']:
            ThemeStaff.objects.create(user=user)

        messages.success(
            self.request, '統一テーマ案投票担当スタッフを登録しました！'
        )

        return super().form_valid(form)


class ThemeSlackView(ThemeStaffOnlyMixin, generic.CreateView):
    template_name = 'theme/submit_slack.html'
    model = ThemeSlack
    form_class = ThemeSlackForm
    success_url = reverse_lazy('theme:staff_menu')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["asis"] = self.asis
        return context

    def get_form(self):
        form = super().get_form()

        if self.asis:
            form.fields['slack_ch'].initial = self.asis.slack_ch

        return form

    def form_valid(self, form):
        messages.success(self.request, 'slack ch. を登録しました！')
        return super().form_valid(form)

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # 現時点での ThemeSlack があれば取得（なければ None）
        self.asis = ThemeSlack.objects.all().first()


class ThemeSlackDeleteView(ThemeStaffOnlyMixin, generic.RedirectView):
    pattern_name = 'theme:staff_menu'

    def get_redirect_url(self, *args, **kwargs):
        # 削除
        obj = get_object_or_404(ThemeSlack)
        obj.delete()

        messages.error(self.request, 'slack ch. を削除しました！')

        # args / kwargs は捨てる
        return super().get_redirect_url()
