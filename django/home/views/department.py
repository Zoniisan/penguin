from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from home.forms import DepartmentForm
from home.models import Department
from penguin import mixins
from penguin.views import OrderFormView


class ListView(mixins.AdminOnlyMixin, OrderFormView):
    template_name = 'home/department_list.html'
    success_url = reverse_lazy('home:department_list')
    model = Department


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
