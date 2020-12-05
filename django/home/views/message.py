from django.conf import settings
from django.contrib import messages
from django.shortcuts import Http404, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views import generic
from home.forms import MessageForm
from home.models import Contact, Message, MessageRead, User
from home.tasks import send_mail_async
from penguin import mixins


class ListView(mixins.IdentifiedOnlyMixin, generic.TemplateView):
    template_name = 'home/message_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # message: メッセージ, is_read: (bool) 既読なら True
        context["object_list"] = [{
            'message': message,
            'is_read': message.is_read_by(self.request.user)
        } for message in Message.objects.filter(to=self.request.user)]

        return context


class DetailView(mixins.IdentifiedOnlyMixin, generic.DetailView):
    template_name = 'home/message_detail.html'
    model = Message

    def get(self, request, **kwargs):
        # message を取得
        message = Message.objects.get(id=kwargs['pk'])

        # 既読情報がなければ登録
        obj, created = MessageRead.objects.get_or_create(
            message=message,
            user=request.user
        )

        # もし今回既読情報を追加した場合はアラート表示
        if created:
            messages.success(request, '開封しました！')

        return super().get(request, **kwargs)


class StaffListView(mixins.StaffOnlyMixin, generic.TemplateView):
    template_name = 'home/message_staff_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # request.user が所属する部局担当
        department_list = self.request.user.department_list()

        # 所属する部局担当を出力
        context['department_list'] = department_list

        # 部局担当ごとにメッセージを抽出
        # department: 部局担当, message_list: その部局担当が送信したメッセージ
        context['object_dict'] = [
            {
                'department': department,
                'message_list': Message.objects.filter(department=department)
            }
            for department in department_list
        ]

        return context


class StaffCreateView(mixins.StaffOnlyMixin, generic.CreateView):
    """メッセージを作成

    kwargs['mode'] によって挙動が異なる
    - 'normal': 宛先をユーザーでが指定
    - 'all': 宛先は個人情報を入力したすべてのユーザー
    - 'contact' お問い合わせへの返信

    'contact' にする場合、kwargs['arg'] で
    返信先への Contact の id を投げる必要がある。
    """
    template_name = 'home/message_staff_create.html'
    model = Message
    form_class = MessageForm
    success_url = reverse_lazy('home:message_staff_list')

    def get_form(self):
        # ユーザーが所属する部局担当のみ選択可能
        form = super().get_form()
        form.fields['department'].queryset = \
            self.request.user.department_list()

        # all モードの場合は個人情報を入力した全 user を宛先とする。
        if self.mode == 'all':
            form.fields['to'].initial = [
                user for user in User.objects.all() if user.is_identified
            ]

        # contact モードの場合...
        if self.mode == 'contact':
            # お問い合わせの送信者を宛先とする。
            form.fields['to'].initial = [self.contact.writer]
            # タイトルを「お問い合わせへの返信」にする。
            form.fields['subject'].initial = 'お問い合わせへの返信'
            # 本文はお問い合わせの内容を引用する。
            form.fields['body'].initial = '\n\nお問い合わせの内容--------\n{0}'.format(
                self.contact.body
            )

        return form

    def form_valid(self, form):
        # 送信者を登録
        form.instance.writer = self.request.user

        # 先回りで Message を保存
        # （Email に内容を記載したいから）
        self.object = form.save()

        # contact モードの場合
        if self.mode == 'contact':
            # 対応完了登録
            self.contact.is_finished = True

            # Contact に 返信メッセージを追加
            self.contact.message.add(self.object)
            self.contact.save()

            # success_url を変更
            self.success_url = reverse_lazy('home:contact_list')

        # 受信者にメールを送信
        self.send_mail(self.object)

        messages.success(self.request, 'メッセージを送信しました！')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # モードを出力
        context['mode'] = self.mode

        # contact モードの場合は contact を出力
        if self.mode == 'contact':
            context['contact'] = self.contact

        return context

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)

        # 想定されるモード
        mode_list = ['normal', 'all', 'contact']

        # モードを設定
        if kwargs['mode'] in mode_list:
            self.mode = kwargs['mode']
        else:
            # 想定外のモードが指定された場合は Http404
            raise Http404

        # contact モードの場合は返信先の Contact のインスタンスを取得
        if self.mode == 'contact':
            self.contact = Contact.objects.get(id=kwargs['arg'])

    def send_mail(self, message):
        """メールを送信する

        Args:
            message(Message): Message のインスタンス
        Returns:
            None
        """
        send_mail_async.delay(
            message.subject, [{
                'recipient': user.email,
                'message': render_to_string(
                    'home/mail/message.html',
                    {
                        'user': user,
                        'message': message,
                        'BASE_URL': settings.BASE_URL
                    }
                )
            } for user in message.to.all()]
        )


class StaffDetailView(mixins.StaffOnlyMixin, generic.DetailView):
    template_name = 'home/message_staff_detail.html'
    model = Message


class StaffReadListView(mixins.StaffOnlyMixin, generic.TemplateView):
    """あるメッセージの全宛先とそのそれぞれの既読状況を集計

    Message.to と MessageRead の情報を突き合わせる
    """
    template_name = 'home/message_staff_readlist.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # message, user を取得
        message = get_object_or_404(Message, id=kwargs['pk'])

        context['message'] = message

        # user: Message.to 内の User, read: MessageRead
        context["object_list"] = [{
            'user': user,
            'read': MessageRead.objects.filter(message=message, user=user)
        } for user in message.to.all()]

        return context
