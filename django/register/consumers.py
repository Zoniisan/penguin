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
        self.group_name = 'token-group'
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

        # src を返す
        return 'data:image/png;base64,{0}'.format(b64), url


class RegistrationConsumer(WebsocketConsumer):
    def connect(self):
        # group に channel を登録
        self.group_name = 'registration-group'
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
        # 企画登録状況を更新
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'send_registration',
            }
        )

    def send_registration(self, event):
        # JSON 形式で登録企画に関する情報を通知
        self.send(text_data=json.dumps({
            'waiting': [{
                'call_id': registration.call_id,
                'kind': str(registration.kind),
                'str': str(registration)
            } for registration in
                Registration.objects.filter(status='waiting')
                .order_by('call_id')
            ],
            'called': [{
                'window-name': window.name
            } for window in Window.objects.all().order_by('name')]
        }))
