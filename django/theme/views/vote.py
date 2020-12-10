import random

from bootstrap_datepicker_plus import DateTimePickerInput
from django import forms
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from theme.forms import NoneForm, VoteScheduleForm
from theme.models import Eptid, Theme, Vote, VoteSchedule
from theme.views import ThemeStaffOnlyMixin


class ScheduleCreateView(ThemeStaffOnlyMixin, generic.CreateView):
    template_name = 'theme/vote_schedule_create.html'
    model = VoteSchedule
    form_class = VoteScheduleForm
    success_url = reverse_lazy('theme:staff_menu')

    def get_form(self):
        form = super().get_form()

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
        messages.success(self.request, '投票日程を登録しました！')
        return super().form_valid(form)


class ScheduleUpdateView(ThemeStaffOnlyMixin, generic.UpdateView):
    template_name = 'theme/vote_schedule_update.html'
    model = VoteSchedule
    form_class = VoteScheduleForm
    success_url = reverse_lazy('theme:staff_menu')

    def get_form(self):
        form = super().get_form()

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
        messages.success(self.request, '投票日程を編集しました！')
        return super().form_valid(form)


class ScheduleDeleteView(ThemeStaffOnlyMixin, generic.RedirectView):
    pattern_name = 'theme:staff_menu'

    def get_redirect_url(self, *args, **kwargs):
        # 削除
        obj = get_object_or_404(VoteSchedule, id=kwargs['pk'])
        obj.delete()

        messages.error(self.request, '投票日程を削除しました！')

        # args / kwargs は捨てる
        return super().get_redirect_url()


class ListPendingView(ThemeStaffOnlyMixin, generic.FormView):
    template_name = 'theme/vote_list_pending.html'
    form_class = NoneForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # VoteSchedule を method で使えるようにする
        self.vote_schedule = \
            get_object_or_404(VoteSchedule, id=kwargs['vote_schedule_id'])

        # 統一テーマの一覧を取得
        # 結果を取得する VoteSchedule（なくてもいい）
        result_schedule_id = kwargs.get('result_vote_schedule_id')
        if result_schedule_id:
            self.result_schedule = \
                get_object_or_404(VoteSchedule, id=result_schedule_id)
            _theme_list = get_theme_list(self.result_schedule)
            self.theme_list = [
                obj['theme'] for obj in _theme_list
            ]
        else:
            self.result_schedule = None
            self.theme_list = Theme.objects.all().order_by('create_datetime')

    def get(self, request, **kwargs):
        # 投票期間前の投票についてのみこの操作を行える
        if self.vote_schedule.get_status() != 'pending':
            raise PermissionDenied

        return super().get(request, **kwargs)

    def get_form(self):
        form = super().get_form()

        # 統一テーマ案 1 件に付き 1 つずつフォームを作る
        for theme in self.theme_list:
            form.fields['obj-{0}'.format(theme.id)] = forms.BooleanField(
                initial=theme in self.vote_schedule.theme_list.all(),
                required=False
            )

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # VoteSchedule を出力
        context['vote_schedule'] = self.vote_schedule
        # フォームのフィールドと統一テーマ案のインスタンスをまとめる
        context['object_list'] = [
            {'field': field, 'theme': theme} for field, theme
            in zip(context['form'], self.theme_list)
        ]
        # 候補となっている統一テーマ案の一覧
        context['active_list'] = self.vote_schedule.theme_list.all()

        # Todo
        context['result_schedule'] = self.result_schedule
        context['finished_vote_schedule_list'] = [
            vote_schedule for vote_schedule in VoteSchedule.objects.all()
            if vote_schedule.get_status() == 'finished'
        ]

        return context

    def form_valid(self, form):
        # 登録
        for key, value in form.cleaned_data.items():
            theme = Theme.objects.get(id=key.replace('obj-', ''))
            if value:
                self.vote_schedule.theme_list.add(theme)
            else:
                self.vote_schedule.theme_list.remove(theme)
        self.vote_schedule.save()

        messages.success(self.request, '候補を確定しました！')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'theme:vote_list_pending',
            kwargs={'vote_schedule_id': self.kwargs['vote_schedule_id']}
        )


class VoteView(UserPassesTestMixin, generic.TemplateView):
    template_name = 'theme/vote.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.vote_schedule = get_object_or_404(VoteSchedule, id=kwargs['pk'])

    def test_func(self):
        # 投票期間内 and 投票済みでない
        return self.vote_schedule.get_status() == 'active' \
            and self.vote_schedule.can_vote_check(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 該当する投票日程を URL から求める
        context['vote_schedule'] = self.vote_schedule

        # 投票候補リストを list で取得
        vote_schedule_list = list(self.vote_schedule.theme_list.all())
        # ランダムに並び替えて出力
        random.shuffle(vote_schedule_list)
        context['object_list'] = vote_schedule_list

        return context


class VoteCreateView(UserPassesTestMixin, generic.RedirectView):
    pattern_name = 'home:index'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.vote_schedule = get_object_or_404(
            VoteSchedule, id=kwargs['vote_schedule_id']
        )
        self.theme = get_object_or_404(
            Theme, id=kwargs['theme_id']
        )

    def test_func(self):
        # 投票期間内 and 投票済みでない
        return self.vote_schedule.get_status() == 'active' \
            and self.vote_schedule.can_vote_check(self.request.user)

    def get_redirect_url(self, *args, **kwargs):
        # Transaction: 票数加算→多重投票禁止措置の順に実行
        with transaction.atomic():
            vote = Vote.objects.create(
                schedule=self.vote_schedule,
                theme=self.theme
            )
            vote.save()

            eptid = Eptid.objects.create(
                schedule=self.vote_schedule,
                eptid=self.request.user.eptid
            )
            eptid.save()

        messages.success(self.request, '投票しました！')

        return super().get_redirect_url()


class ResultView(ThemeStaffOnlyMixin, generic.TemplateView):
    template_name = 'theme/vote_result.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        self.vote_schedule = get_object_or_404(
            VoteSchedule, id=kwargs['vote_schedule_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 該当する投票日程を URL から求める
        context['vote_schedule'] = self.vote_schedule

        # 統一テーマ案を票数順に取得
        context['theme_list'] = get_theme_list(self.vote_schedule)
        return context


def get_theme_list(vote_schedule):
    """投票日程→統一テーマ案のリストに変換

    統一テーマ案を票数順に表示

    Args:
        vote_schedule(VoteSchedule): 投票日程
    Returns:
        list<dict>: [{'theme': Theme, 'count': int}]
        count = 獲得票数順に表示
    """
    # theme, count を取得
    theme_list = [{
        'theme': theme,
        'count': theme.get_count(vote_schedule)
    } for theme in vote_schedule.theme_list.all()]

    # 票数順に並び替え
    return sorted(theme_list, key=lambda x: x['count'], reverse=True)
