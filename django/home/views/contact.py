from django.conf import settings
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django_slack import slack_message
from home.forms import ContactForm
from home.models import Contact, ContactKind
from penguin import mixins


class CreateView(mixins.RedirectIfNotIdentified, generic.CreateView):
    template_name = 'home/contact_create.html'
    model = Contact
    form_class = ContactForm
    success_url = reverse_lazy('home:index')

    def form_valid(self, form):
        # 担当者を登録
        form.instance.writer = self.request.user

        # 先回りで Contact を登録（id を取得）
        self.object = form.save()

        # 対応する部局担当に slack を送信
        self.send_slack(self.object)

        messages.success(self.request, 'お問い合わせを送信しました！')
        return super().form_valid(form)

    def send_slack(self, contact):
        """対応する slack ch. に slack を送信

        Args:
            contact(Contact): お問い合わせ
        Returns:
            None
        """
        # attachment: メッセージ下部に表示される要素（ボタンなど）
        attachments = [{
                "fallback": "Contact Received",
                "color": "success",
                "title": "お問い合わせ詳細",
                "actions": [{
                        "type": "button",
                        "name": "go",
                        "text": "対応する",
                        "url": "{0}{1}".format(
                            settings.BASE_URL, reverse_lazy(
                                'home:contact_detail',
                                kwargs={'pk': contact.id}
                            )
                        ),
                        "style": "primary"
                }]
        }]

        # slack を送信
        slack_message('home/slack/contact.slack', {
            'object': contact,
            'slack_channel': contact.kind.verbose_slack_ch()
        }, attachments)


class ListView(mixins.StaffOnlyMixin, generic.TemplateView):
    template_name = 'home/contact_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 所属する部局担当に対応するお問い合わせ種別のリスト
        kind_list = ContactKind.objects.filter(
            department__in=self.request.user.department_list()
        ).distinct()

        context['kind_list'] = kind_list

        # kind: お問い合わせ種別, list: その種別に属するお問い合わせのリスト
        context['object_list'] = [{
            'kind': contactkind,
            'list': contactkind.contact.all()
        } for contactkind in kind_list]

        return context


class DetailView(mixins.StaffOnlyMixin, generic.DetailView):
    template_name = 'home/contact_detail.html'
    model = Contact


class FinishView(mixins.StaffOnlyMixin, generic.RedirectView):
    """対応完了にする

    指定した Contact の is_finished を True とし、対応完了とする。
    PENGUIN のメッセージ機能を用いて返信すると自動的に is_finished = True
    となるが、そうでなくともこの View にアクセスすれば is_finished = True
    となる。
    """
    pattern_name = 'home:contact_detail'

    def get_redirect_url(self, *args, **kwargs):
        obj = get_object_or_404(Contact, id=kwargs['pk'])
        obj.is_finished = True
        obj.save()

        messages.success(self.request, '対応完了にしました！')

        return super().get_redirect_url(*args, **kwargs)
