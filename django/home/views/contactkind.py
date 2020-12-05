from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from home.forms import ContactKindForm
from home.models import ContactKind
from penguin import mixins
from penguin.views import OrderFormView


class ListView(mixins.AdminOnlyMixin, OrderFormView):
    template_name = 'home/contactkind_list.html'
    model = ContactKind
    success_url = reverse_lazy('home:contactkind_list')


class CreateView(mixins.AdminOnlyMixin, generic.CreateView):
    template_name = 'home/contactkind_create.html'
    model = ContactKind
    form_class = ContactKindForm
    success_url = reverse_lazy('home:contactkind_list')

    def form_valid(self, form):
        messages.success(self.request, 'お問い合わせ種別を登録しました！')
        return super().form_valid(form)


class UpdateView(mixins.AdminOnlyMixin, generic.UpdateView):
    template_name = 'home/contactkind_update.html'
    model = ContactKind
    form_class = ContactKindForm
    success_url = reverse_lazy('home:contactkind_list')

    def form_valid(self, form):
        messages.success(self.request, 'お問い合わせ種別を更新しました！')
        return super().form_valid(form)


class DeleteView(mixins.AdminOnlyMixin, generic.RedirectView):
    permanent = True
    pattern_name = 'home:contactkind_list'

    def get_redirect_url(self, *args, **kwargs):
        # 削除
        obj = get_object_or_404(ContactKind, id=kwargs['pk'])
        obj.delete()

        messages.error(self.request, 'お問い合わせ種別を削除しました！')

        # args / kwargs は捨てる
        return super().get_redirect_url()
