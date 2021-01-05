from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from penguin import mixins
from penguin.views import OrderFormView
from project.forms import KindForm
from project.models import Kind


class ListView(mixins.AdminOnlyMixin, OrderFormView):
    template_name = 'project/kind_list.html'
    model = Kind
    success_url = reverse_lazy('project:kind_list')


class CreateView(mixins.AdminOnlyMixin, generic.CreateView):
    template_name = 'project/kind_create.html'
    model = Kind
    form_class = KindForm
    success_url = reverse_lazy('project:kind_list')

    def form_valid(self, form):
        messages.success(self.request, '企画種別を登録しました！')
        return super().form_valid(form)


class UpdateView(mixins.AdminOnlyMixin, generic.UpdateView):
    template_name = 'project/kind_update.html'
    model = Kind
    form_class = KindForm
    success_url = reverse_lazy('project:kind_list')

    def form_valid(self, form):
        messages.success(self.request, '企画種別を更新しました！')
        return super().form_valid(form)


class DeleteView(mixins.AdminOnlyMixin, generic.RedirectView):
    pattern_name = 'project:kind_list'

    def get_redirect_url(self, *args, **kwargs):
        # 削除
        obj = get_object_or_404(Kind, id=kwargs['pk'])
        obj.delete()

        messages.error(self.request, '企画種別を削除しました！')

        # args / kwargs は捨てる
        return super().get_redirect_url()
