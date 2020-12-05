from django import forms
from django.contrib import messages
from django.forms import HiddenInput, IntegerField
from django.views import generic as gv


class PassForm(forms.Form):
    pass


class OrderFormView(gv.FormView):
    form_class = PassForm

    def get_form(self):
        form = super().get_form()
        # field: new_order_obj_i を作成（Hidden 属性）
        for count, obj in enumerate(self.model.objects.all()):
            form.fields['new_order_obj_{0}'.format(obj.id)] = IntegerField(
                widget=HiddenInput(),
                initial=count
            )
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = self.model.objects.all()
        return context

    def form_valid(self, form):
        for key, value in form.cleaned_data.items():
            object_id = key.replace('new_order_obj_', '')
            obj = self.model.objects.get(id=object_id)
            obj.to(value)

        # message
        messages.info(self.request, '順序を変更しました！')
        return super().form_valid(form)
