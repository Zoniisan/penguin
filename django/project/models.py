import uuid

from django.db import models
from ordered_model.models import OrderedModel
from penguin import validators


class Kind(OrderedModel):
    class Meta(OrderedModel.Meta):
        verbose_name = '企画種別'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def verbose_slack_ch(self):
        """slack_ch を # つきで表示

        Returns:
            str: #channel
        """
        return '#{0}'.format(self.slack_ch)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        verbose_name='名前',
        max_length=50
    )

    symbol = models.CharField(
        verbose_name='シンボル',
        max_length=1,
        validators=[validators.symbol_validator],
        help_text='英大文字 1 文字で指定してください',
        unique=True
    )

    class FoodChoice(models.TextChoices):
        TRUE = 'true', '必須'
        FALSE = 'false', '禁止'
        SELECT = 'select', '選択可能'

    food = models.CharField(
        verbose_name='飲食物提供',
        max_length=10,
        choices=FoodChoice.choices
    )

    staff_list = models.ManyToManyField(
        'home.User',
        verbose_name='担当スタッフ'
    )

    slack_ch = models.CharField(
        verbose_name='slack',
        max_length=50,
        help_text='#は除いて登録してください'
    )
