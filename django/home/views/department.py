from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from home.forms import AdminForm, DepartmentForm
from home.models import Department, User
from penguin import mixins
from penguin.views import OrderFormView


class ListView(mixins.AdminOnlyMixin, OrderFormView):
    template_name = 'home/department_list.html'
    success_url = reverse_lazy('home:department_list')
    model = Department

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["admin_list"] = User.objects.filter(is_admin=True)
        return context


class CreateView(mixins.AdminOnlyMixin, generic.CreateView):
    template_name = 'home/department_create.html'
    model = Department
    form_class = DepartmentForm
    success_url = reverse_lazy('home:department_list')

    def form_valid(self, form):
        messages.success(self.request, '部局担当を登録しました！')
        return super().form_valid(form)


class UpdateView(mixins.AdminOnlyMixin, generic.UpdateView):
    template_name = 'home/department_update.html'
    model = Department
    form_class = DepartmentForm
    success_url = reverse_lazy('home:department_list')

    def form_valid(self, form):
        messages.success(self.request, '部局担当を更新しました！')
        return super().form_valid(form)


class DeleteView(mixins.AdminOnlyMixin, generic.RedirectView):
    permanent = True
    pattern_name = 'home:department_list'

    def get_redirect_url(self, *args, **kwargs):
        # 削除
        obj = get_object_or_404(Department, id=kwargs['pk'])
        obj.delete()

        messages.error(self.request, '部局担当を削除しました！')

        # args / kwargs は捨てる
        return super().get_redirect_url()


class AdminView(mixins.AdminOnlyMixin, generic.FormView):
    template_name = 'home/department_admin.html'
    form_class = AdminForm
    success_url = reverse_lazy('home:department_list')

    def get_form(self):
        form = super().get_form()

        # 初期値として現在のシステム管理者をセット
        form.fields['admin_list'].initial = User.objects.filter(is_admin=True)

        return form

    def form_valid(self, form):
        # システム管理者を登録
        for user in User.objects.staff_list():
            user.is_admin = user in form.cleaned_data['admin_list']
            user.save()

        messages.success(self.request, 'システム管理者を登録しました！')

        return super().form_valid(form)
