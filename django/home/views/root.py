from django.views import generic
from home.models import Notice
from theme.models import SubmitSchedule, Theme


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
        context['submit_schedule'] = SubmitSchedule.objects.all().first()
        # 統一テーマ提出可能か判定
        context['can_submit'] = \
            Theme.objects.can_submit_check(self.request.user)
        return context
