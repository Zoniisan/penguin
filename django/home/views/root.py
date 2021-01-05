from django.views import generic
from home.models import Notice
from register.models import Registration
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
        if self.request.user.is_authenticated:
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
            # 企画登録整理番号：待機
            context['waiting_call_id_list'] = \
                Registration.objects.get_call_id_list(
                    self.request.user, 'waiting')
            # 企画登録整理番号：対応中
            context['called_call_id_list'] = \
                Registration.objects.get_call_id_list(
                    self.request.user, 'called')
            # 企画登録整理番号：保留
            context['pending_call_id_list'] = \
                Registration.objects.get_call_id_list(
                    self.request.user, 'pending')
            # 企画登録（企画責任者未確定）
            context['registration_list'] = Registration.objects.filter(
                temp_leader=self.request.user, status='accepted'
            )
        return context
