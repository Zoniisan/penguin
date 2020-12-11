from django.views import generic
from home.models import Notice
from theme.models import SubmitSchedule, Theme, VoteSchedule


class IndexView(generic.TemplateView):
    """ホームページ
    """
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # お知らせ（掲載期間のもののみ順次表示）
        context['notice_list'] = [
            notice for notice in Notice.objects.all() if notice.is_active()
        ]
        # 統一テーマ提出期間内であれば表示
        context['submit_schedule_is_active'] = \
            SubmitSchedule.objects.is_active()
        context['submit_schedule'] = SubmitSchedule.objects.all().first()
        # 統一テーマ提出可能か判定
        context['can_submit'] = \
            Theme.objects.can_submit_check(self.request.user)
        # 統一テーマ案投票日程
        context['vote_schedule_dict'] = [{
            'vote_schedule': vote_schedule,
            'can_vote': vote_schedule.can_vote_check(self.request.user)
        } for vote_schedule in VoteSchedule.objects.all()
            if vote_schedule.get_status() == 'active'
        ]

        return context
