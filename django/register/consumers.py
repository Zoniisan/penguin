import base64
import json
from io import BytesIO

import qrcode
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from django.urls import reverse_lazy

from register.models import Registration, VerifyToken, Window


class TokenConsumer(WebsocketConsumer):
    def connect(self):
        # group に channel を登録
        self.group_name = 'token_group'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        # 通信を許可
        self.accept()

    def disconnect(self, close_code):
        # channel を group から外す
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        # token を更新
        verify_token = VerifyToken.objects.create()
        # staff.SignageView を閲覧中のブラウザに対し、
        # 新しいトークンの情報を通知
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'send_token',
                'token': str(verify_token.id),
                'create_datetime': verify_token.create_datetime.strftime(
                    '%Y/%m/%d %H:%M:%S'
                )
            }
        )

    def send_token(self, event):
        # JSON 形式でトークンに関する情報を通知
        qrcode, url = self.get_qrcode(event['token'])
        self.send(text_data=json.dumps({
            'qrcode': qrcode,
            'url': url,
            'create_datetime': event['create_datetime']
        }))

    def get_qrcode(self, token):
        """token から qrcode を base64 形式で取得
        """
        # URL を取得
        url = ''.join([
            settings.BASE_URL,
            str(reverse_lazy(
                'register:verify', kwargs={'token': token}
            ))
        ])

        # qrcode の base64 を作成
        qr = qrcode.QRCode(box_size=5)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image()
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # base64 形式の qrcode と、その URL を返す
        return 'data:image/png;base64,{0}'.format(b64), url


class RegistrationConsumer(WebsocketConsumer):
    def connect(self):
        # group に channel を登録
        self.group_name = 'registration_group'
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        # 通信を許可
        self.accept()

    def disconnect(self, close_code):
        # channel を group から外す
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def receive(self, text_data):
        # 直前に呼出操作を行った窓口があれば、その ID を取得
        text_data_json = json.loads(text_data)
        call_window_id = text_data_json.get('call_window_id')

        # 企画登録状況を更新
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'send_registration',
                'call_window_id': call_window_id
            }
        )

    def send_registration(self, event):
        # 待機企画登録リスト
        waiting_list = Registration.objects.filter(
            status='waiting').order_by('call_id')
        # 保留企画登録リスト
        pending_list = Registration.objects.filter(
            status='pending').order_by('call_id')

        # JSON 形式で登録企画に関する情報を通知
        self.send(text_data=json.dumps({
            # 待機企画リスト
            'waiting': [{
                'id': str(registration.id),
                'call_id': registration.call_id,
                'kind': str(registration.kind),
                'kind_id': str(registration.kind.id),
                'str': str(registration),
                'temp_leader': str(registration.temp_leader)
            } for registration in waiting_list],
            # 保留企画リスト
            'pending': [{
                'id': str(registration.id),
                'call_id': registration.call_id,
                'kind': str(registration.kind),
                'kind_id': str(registration.kind.id),
                'str': str(registration),
                'temp_leader': str(registration.temp_leader)
            } for registration in pending_list],
            # 開設している窓口リスト
            'windows': [{
                'id': str(window.id),
                'name': window.name,
                'call_id': window.registration.call_id\
                if window.registration else '---',
                'staff': str(window.staff),
                'kind': str(window.registration.kind\
                        if window.registration else '---'),
                'kind_id': str(window.registration.kind.id\
                        if window.registration else '---'),
                'str': str(window.registration\
                        if window.registration else '---'),
                'temp_leader': str(window.registration.temp_leader\
                        if window.registration else '---'),
                'register_id': str(window.registration.id\
                        if window.registration else '---')
            } for window in Window.objects.all().order_by('name')],
            # 直前に呼出操作を行った窓口の ID があれば渡す
            'call_window_id': event['call_window_id']
        }))
