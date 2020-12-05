from celery import shared_task
from django.conf import settings
from django.core.mail import send_mass_mail


@shared_task
def send_mail_async(subject, obj_list):
    """非同期でメールを一斉送信

    Celery を用いてメールを非同期に一斉送信する。
    context['user'] に受信者の User インスタンスが自動登録される。

    Args:
        subject(str): タイトル
        obj_list(list<dict>):[{'recipient', 'message'}]
        （Celery task は json-like な値しか受理できない）

    Return:
        None
    """
    # メールを送信
    # send_mass_mail の引数は list ではなく tuple
    send_mass_mail(tuple([
        (subject, obj['message'], settings.EMAIL_FROM, [obj['recipient']])
        for obj in obj_list
    ]))
