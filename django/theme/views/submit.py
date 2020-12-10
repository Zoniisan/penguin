from bootstrap_datepicker_plus import DateTimePickerInput
from countable_field.widgets import CountableWidget
from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django_slack import slack_message
from penguin.mixins import RedirectIfNotIdentified
from theme.forms import StaffSubmitForm, SubmitScheduleForm, ThemeForm
from theme.models import SubmitSchedule, Theme, ThemeSlack
from theme.views import ThemeStaffOnlyMixin


class SubmitView(RedirectIfNotIdentified, generic.CreateView):
    """通常提出

    1 ユーザーに限り 1 件まで統一テーマ案を提出できる
    """
    template_name = 'theme/submit_submit.html'
    model = Theme
    form_class = ThemeForm
    success_url = reverse_lazy('home:index')

    def get(self, request, **kwargs):
        # 提出済みの場合は拒否
        if not Theme.objects.can_submit_check(request.user):
            messages.error(request, 'あなたは既に統一テーマ案を提出済みです。')
            return redirect('home:index')
        # 投票期間外
        if not SubmitSchedule.objects.is_active():
            messages.error(request, '統一テーマ案提出日程外です。')
            return redirect('home:index')

        return super().get(request, **kwargs)

    def get_form(self):
        form = super().get_form()

        # 文字数カウント
        form.fields['theme'].widget = CountableWidget(attrs={
            'data-count': 'characters',
            'data-max-count': 100,
        })
        form.fields['description'].widget = CountableWidget(attrs={
            'data-count': 'characters',
            'data-max-count': 400,
        })

        return form

    def form_valid(self, form):
        # 投稿者登録
        form.instance.writer = self.request.user

        # slack を送信
        self.send_slack(form.instance)

        messages.success(self.request, '統一テーマ案を提出しました！')
        return super().form_valid(form)

    def send_slack(self, theme):
        """対応する slack ch. に slack を送信

        slack ch. が登録されていない場合は送信しない

        Args:
            theme(Theme): 統一テーマ案
        Returns:
            None
        """
        slack = ThemeSlack.objects.all().first()

        if slack:
            # attachment: メッセージ下部に表示される要素（ボタンなど）
            attachments = [{
                "fallback": "Theme Submitted",
                "color": "success",
                "title": "統一テーマ案一覧",
                "actions": [{
                    "type": "button",
                            "name": "go",
                            "text": "統一テーマ案一覧を閲覧する",
                            "url": "{0}{1}".format(
                                settings.BASE_URL, reverse_lazy(
                                    'theme:submit_list'
                                )
                            ),
                    "style": "primary"
                }]
            }]

            # slack を送信
            slack_message('theme/slack/submitted.slack', {
                'object': theme,
                'slack_ch': slack.verbose_slack_ch()
            }, attachments)


class StaffSubmitView(ThemeStaffOnlyMixin, generic.CreateView):
    """強制提出

    統一テーマ案投票担当スタッフであれば強制的に提出できる
    投稿者についても自由に指定できる
    この場合、強制提出操作を行ったスタッフが記録される
    """
    template_name = 'theme/submit_staff_submit.html'
    model = Theme
    form_class = StaffSubmitForm
    success_url = reverse_lazy('theme:submit_list')

    def get_form(self):
        form = super().get_form()

        # 文字数カウント
        form.fields['theme'].widget = CountableWidget(attrs={
            'data-count': 'characters',
            'data-max-count': 100,
        })
        form.fields['description'].widget = CountableWidget(attrs={
            'data-count': 'characters',
            'data-max-count': 400,
        })

        return form

    def form_valid(self, form):
        # 強制提出を行ったスタッフが記録される
        form.instance.submit_staff = self.request.user

        messages.success(self.request, '統一テーマ案を提出しました！')
        return super().form_valid(form)


class ScheduleView(ThemeStaffOnlyMixin, generic.CreateView):
    template_name = 'theme/submit_schedule.html'
    model = SubmitSchedule
    form_class = SubmitScheduleForm
    success_url = reverse_lazy('theme:staff_menu')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["asis"] = self.asis
        return context

    def get_form(self):
        form = super().get_form()

        if self.asis:
            form.fields['start_datetime'].initial = self.asis.start_datetime
            form.fields['finish_datetime'].initial = self.asis.finish_datetime

        # datetimepicker を用意
        # datetimepicker は views.py 側で widget 設定を行わないとだめっぽい
        form.fields['start_datetime'].widget = DateTimePickerInput(options={
            'format': 'YYYY-MM-DD HH:mm',
            'locale': 'ja'
        }).start_of('schedule')

        form.fields['finish_datetime'].widget = DateTimePickerInput(options={
            'format': 'YYYY-MM-DD HH:mm',
            'locale': 'ja'
        }).end_of('schedule')

        return form

    def form_valid(self, form):
        messages.success(self.request, '投票期間を登録しました！')
        return super().form_valid(form)

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # 現時点での SubmitSchedule があれば取得（なければ None）
        self.asis = SubmitSchedule.objects.filter().first()


class ScheduleDeleteView(ThemeStaffOnlyMixin, generic.RedirectView):
    pattern_name = 'theme:staff_menu'

    def get_redirect_url(self, *args, **kwargs):
        # 削除
        obj = get_object_or_404(SubmitSchedule)
        obj.delete()

        messages.error(self.request, '投票期間を削除しました！')

        # args / kwargs は捨てる
        return super().get_redirect_url()


class ListView(ThemeStaffOnlyMixin, generic.ListView):
    template_name = 'theme/submit_list.html'
    model = Theme
    ordering = ['create_datetime']


class UpdateView(ThemeStaffOnlyMixin, generic.UpdateView):
    template_name = 'theme/submit_update.html'
    model = Theme
    form_class = ThemeForm
    success_url = reverse_lazy('theme:submit_list')

    def get_form(self):
        form = super().get_form()

        # 文字数カウント
        form.fields['theme'].widget = CountableWidget(attrs={
            'data-count': 'characters',
            'data-max-count': 100,
        })
        form.fields['description'].widget = CountableWidget(attrs={
            'data-count': 'characters',
            'data-max-count': 400,
        })

        return form

    def form_valid(self, form):
        # 最終編集を行ったスタッフが記録される
        form.instance.update_staff = self.request.user

        messages.success(self.request, '統一テーマ案を編集しました！')
        return super().form_valid(form)


class DeleteView(ThemeStaffOnlyMixin, generic.RedirectView):
    pattern_name = 'theme:submit_list'

    def get_redirect_url(self, *args, **kwargs):
        # 削除
        obj = get_object_or_404(Theme, id=kwargs['pk'])
        obj.delete()

        messages.error(self.request, '統一テーマ案を削除しました！')

        # args / kwargs は捨てる
        return super().get_redirect_url()
