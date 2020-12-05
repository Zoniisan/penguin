from django.views import generic
from home.models import Notice


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
        return context
