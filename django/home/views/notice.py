import datetime

from bootstrap_datepicker_plus import DateTimePickerInput
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from home.forms import NoticeForm
from home.models import Notice
from penguin import mixins


class ListView(mixins.AdminOnlyMixin, generic.TemplateView):
    template_name = 'home/notice_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 現在時刻
        context['datetime_now'] = datetime.datetime.now()
        # 全てのお知らせ
        context['notice_list'] = Notice.objects.all()
        # アクティブなお知らせ
        context['active_notice_list'] = [
            notice for notice in Notice.objects.all() if notice.is_active()
        ]
        return context


class CreateView(mixins.AdminOnlyMixin, generic.CreateView):
    template_name = 'home/notice_create.html'
    model = Notice
    form_class = NoticeForm
    success_url = reverse_lazy('home:notice_list')

    def get_form(self):
        # datetimepicker を用意
        # datetimepicker は views.py 側で widget 設定を行わないとだめっぽい
        form = super().get_form()

        form.fields['start_datetime'].widget = DateTimePickerInput(options={
            'format': 'YYYY-MM-DD HH:mm',
            'locale': 'ja'
        }).start_of('display')

        form.fields['finish_datetime'].widget = DateTimePickerInput(options={
            'format': 'YYYY-MM-DD HH:mm',
            'locale': 'ja'
        }).end_of('display')

        return form

    def form_valid(self, form):
        # 担当者を登録
        form.instance.writer = self.request.user

        messages.success(self.request, 'お知らせを登録しました！')
        return super().form_valid(form)


class UpdateView(mixins.AdminOnlyMixin, generic.UpdateView):
    template_name = 'home/notice_update.html'
    model = Notice
    form_class = NoticeForm
    success_url = reverse_lazy('home:notice_list')

    def get_form(self):
        form = super().get_form()

        form.fields['start_datetime'].widget = DateTimePickerInput(options={
            'format': 'YYYY-MM-DD HH:mm',
            'locale': 'ja'
        }).start_of('display')
        form.fields['finish_datetime'].widget = DateTimePickerInput(options={
            'format': 'YYYY-MM-DD HH:mm',
            'locale': 'ja'
        }).end_of('display')

        return form

    def form_valid(self, form):
        # 担当者を登録
        form.instance.writer = self.request.user

        messages.success(self.request, 'メッセージを登録しました！')
        return super().form_valid(form)


class DeleteView(mixins.AdminOnlyMixin, generic.RedirectView):
    pattern_name = 'home:notice_list'

    def get_redirect_url(self, *args, **kwargs):
        # 削除
        obj = get_object_or_404(Notice, id=kwargs['pk'])
        obj.delete()

        messages.error(self.request, 'お知らせを削除しました！')

        # args / kwargs は捨てる
        return super().get_redirect_url()
