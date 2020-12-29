import base64
import json
from io import BytesIO

import qrcode
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.conf import settings
from django.urls import reverse

from register.models import VerifyToken


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
        # staff.SignageView を閲覧中のブラウザに対し、
        # 新しいトークンの情報を通知
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'send_token',
            }
        )

    def send_token(self, event):
        # token を更新
        verify_token = VerifyToken.objects.create()

        # JSON 形式でトークンに関する情報を通知
        self.send(text_data=json.dumps({
            'qrcode': self.get_qrcode(verify_token),
            'create_datetime': verify_token.create_datetime.strftime(
                '%Y/%m/%d %H:%M:%S'
            )
        }))

    def get_qrcode(self, verify_token):
        """token から qrcode を base64 形式で取得
        """
        # URL を取得
        text = ''.join([
            settings.BASE_URL,
            reverse('home:index'),
            str(verify_token.id)
        ])

        # qrcode の base64 を作成
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=4,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image()
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # src を返す
        return 'data:image/png;base64,{0}'.format(b64)
