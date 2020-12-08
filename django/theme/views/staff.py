from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views import generic
from theme.forms import ThemeStaffForm
from theme.models import ThemeStaff


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
        context["theme_staff_list"] = ThemeStaff.objects.all_list()
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
