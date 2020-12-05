from django import template
from home.models import Message, User

register = template.Library()


@register.simple_tag(takes_context=True)
def message_alert(context, user_id):
    """あるユーザーの未読メッセージ件数を取得

    Args:
        user(str): ユーザーの id
    Returns:
        str: 空文字
    """
    if user_id:
        user = User.objects.get(id=user_id)
        # 未読のメッセージの件数を数える
        context['unread_message_count'] = len([
            message for message in Message.objects.filter(to=user)
            if not message.is_read_by(user)
        ])
    else:
        # そもそもユーザーがログインしていない場合は 0 を返す
        context['unread_message_count'] = 0

    # 返り値なし（タグの場所には何も表示しない）
    return ''
