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


class ScheduleBaseView(ThemeStaffOnlyMixin):
    """投票日程の作成・更新を行うためのベースクラス

    作成・更新時の共通項をこのクラスにまとめる
    """
    model = VoteSchedule
    form_class = VoteScheduleForm
    success_url = reverse_lazy('theme:staff_menu')

    def get_form(self):
        form = super().get_form()

        # datetimepicker を用意
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


class ScheduleCreateView(ScheduleBaseView, generic.CreateView):
    """投票日程を作成
    """
    template_name = 'theme/vote_schedule_create.html'


class ScheduleUpdateView(ScheduleBaseView, generic.UpdateView):
    """投票日程を更新
    """
    template_name = 'theme/vote_schedule_update.html'


class ScheduleDeleteView(ThemeStaffOnlyMixin, generic.RedirectView):
    pattern_name = 'theme:staff_menu'

    def get_redirect_url(self, *args, **kwargs):
        # 削除
        obj = get_object_or_404(VoteSchedule, id=kwargs['pk'])
        obj.delete()

        messages.error(self.request, '投票日程を削除しました！')

        # args / kwargs は捨てる
        return super().get_redirect_url()


class ListView(UserPassesTestMixin, generic.TemplateView):
    """投票候補一覧画面

    候補となる統一テーマ案をランダムな並び順で表示
    """
    template_name = 'theme/vote_list.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # URL で指定された VoteSchedule のインスタンス
        self.vote_schedule = \
            get_object_or_404(VoteSchedule, id=kwargs['vote_schedule_id'])

    def test_func(self):
        # 投票期間内 and 投票済みでない
        return self.vote_schedule.get_status() == 'active' \
            and self.vote_schedule.can_vote_check(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # VoteSchedule のインスタンス
        context['vote_schedule'] = self.vote_schedule

        # 投票候補リストを list で取得
        # この時点では投稿日時順に並んでいる
        sorted_theme_list = list(self.vote_schedule.theme_list.all())

        # ランダムに並び替えて出力
        context['theme_list'] = \
            random.sample(sorted_theme_list, len(sorted_theme_list))

        return context


class CreateView(UserPassesTestMixin, generic.RedirectView):
    """投票処理

    実際に投票処理を行う
    """
    pattern_name = 'home:index'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # 投票する VoteSchedule のインスタンスを url から取得
        self.vote_schedule = get_object_or_404(
            VoteSchedule, id=kwargs['vote_schedule_id']
        )
        # 投票する Theme のインスタンスを url から取得
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
            # 票数加算
            vote = Vote.objects.create(
                schedule=self.vote_schedule,
                theme=self.theme
            )
            vote.save()

            # 多重投票禁止登録（eptid を登録）
            eptid = Eptid.objects.create(
                schedule=self.vote_schedule,
                eptid=self.request.user.eptid
            )
            eptid.save()

        messages.success(self.request, '投票しました！')

        return super().get_redirect_url()


class CandidateView(ThemeStaffOnlyMixin, generic.FormView):
    """ある投票日程の候補となる統一テーマ案を選択する

    result_vote_schedule_id が指定されている
        →その投票日程の候補から、今回の候補を選択。
        　　　　統一テーマはこの投票日程の得票数順に表示される。
    otherwise
        →全ての提出された統一テーマ案から、今回の候補を選択。
        　　　　統一テーマは投稿日時順に表示される。
    """
    template_name = 'theme/vote_candidate.html'
    form_class = NoneForm

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        # 候補を選択する投票日程 VoteSchedule のインスタンス
        self.vote_schedule = \
            get_object_or_404(VoteSchedule, id=kwargs['vote_schedule_id'])

        # 結果を取得する投票日程 VoteSchedule のインスタンス (Optional)
        # これが指定されている場合、候補はこの日程の候補から選択する。
        # また、統一テーマ案はこの日程の得票数順に表示される。
        result_vote_schedule_id = kwargs.get('result_vote_schedule_id')
        self.result_vote_schedule = \
            get_object_or_404(VoteSchedule, id=result_vote_schedule_id) \
            if result_vote_schedule_id else None

        # 画面に表示する統一テーマ案のリスト
        self.theme_count_list = get_theme_count_list(self.result_vote_schedule)

    def get(self, request, **kwargs):
        # 投票期間前の投票についてのみこの操作を行える
        if self.vote_schedule.get_status() != 'pending':
            raise PermissionDenied

        return super().get(request, **kwargs)

    def get_form(self):
        form = super().get_form()

        # 統一テーマ案 1 件に付き 1 つずつフォームを作る
        for theme_count in self.theme_count_list:
            # theme_count から統一テーマ theme を取り出す
            theme = theme_count['theme']
            # フィールド作成（既に候補になっている場合は初期値 True とする）
            # id は Theme のインスタンスの id をそのまま採用
            # ただし str 型にキャストしないと内部エラーが発生する
            form.fields[str(theme.id)] = forms.BooleanField(
                initial=theme in self.vote_schedule.theme_list.all(),
                required=False
            )

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 候補を選択する VoteSchedule を出力
        context['vote_schedule'] = self.vote_schedule

        # 結果を取得する VoteSchedule を出力
        context['result_vote_schedule'] = self.result_vote_schedule

        # 結果を取得できる（終了した） VoteSchedule のリストを出力
        context['finished_vote_schedule_list'] = [
            vote_schedule for vote_schedule in VoteSchedule.objects.all()
            if vote_schedule.get_status() == 'finished'
        ]

        # フォームのフィールドと統一テーマ案/票数のインスタンスをまとめる
        context['object_list'] = [
            {'field': field, 'theme_count': theme_count} for field, theme_count
            in zip(context['form'], self.theme_count_list)
        ]

        # 画面読み込み時点で候補となっている統一テーマ案の一覧
        context['active_theme_list'] = self.vote_schedule.theme_list.all()

        return context

    def form_valid(self, form):
        # form に入力された内容に応じて、候補を登録
        for key, value in form.cleaned_data.items():
            # フォームのフィールド名は Theme のインスタンスの id
            # よってこの値を用いて統一テーマを取得する
            theme = Theme.objects.get(id=key)

            if value:
                # チェックが入っている場合は候補に入れる
                self.vote_schedule.theme_list.add(theme)
            else:
                # そうでない場合は候補から外す
                self.vote_schedule.theme_list.remove(theme)

        self.vote_schedule.save()
        messages.success(self.request, '候補を確定しました！')
        return super().form_valid(form)

    def get_success_url(self):
        # vote_schedule_id を保持
        kwargs = {'vote_schedule_id': self.vote_schedule.id}

        if self.result_vote_schedule:
            # result_vote_schedule_id が url で指定されている場合は
            # それも保持する
            kwargs['result_vote_schedule_id'] = self.result_vote_schedule.id

        return reverse_lazy('theme:vote_candidate', kwargs=kwargs)


class ResultView(ThemeStaffOnlyMixin, generic.TemplateView):
    """投票結果を表示

    投票中の場合は「速報」終了後の場合は「結果」として表示
    （どちらも表示内容はほぼ変わらない）
    """
    template_name = 'theme/vote_result.html'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # VoteSchedule のインスタンスを url から取得
        self.vote_schedule = get_object_or_404(
            VoteSchedule, id=kwargs['vote_schedule_id']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 投票日程
        context['vote_schedule'] = self.vote_schedule

        # 統一テーマ案を票数順に取得
        context['theme_list'] = get_theme_count_list(self.vote_schedule)

        return context


def get_theme_count_list(vote_schedule=None):
    """投票日程→統一テーマ案のリストに変換

    統一テーマ案を票数順に表示する。
    （Returns の形式に注意）

    投票日程 vote_schedule を与えなかった場合は
    統一テーマ案を全て返し、票数は全て 0 とする。

    Args:
        vote_schedule(VoteSchedule): 投票日程
    Returns:
        list<dict>: [{'theme': Theme, 'count': int}]
        count = 獲得票数順に表示
    """
    if vote_schedule:
        # 投票日程が与えられた→候補の theme と票数 count を取得
        theme_count_list = [{
            'theme': theme,
            'count': theme.get_count(vote_schedule)
        } for theme in vote_schedule.theme_list.all()]
    else:
        # 投票日程が与えられなかった→全ての theme と票数 0 を取得
        theme_count_list = [{
            'theme': theme,
            'count': 0
        } for theme in Theme.objects.all()]

    # 票数順に並び替え
    return sorted(theme_count_list, key=lambda x: x['count'], reverse=True)
