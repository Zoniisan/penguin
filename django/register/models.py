import uuid

from django.core.validators import RegexValidator
from django.db import models
from home.models import User
from penguin import validators


class Registration(models.Model):
    class Meta():
        verbose_name = '企画登録'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0}: {1}'.format(self.verbose_id, self.group)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    verbose_id_validator = RegexValidator(
        regex=r'^x[A-Z]\-[0-9]{3}$',
        message='形式が不正です！ Ex. xA-000'
    )

    verbose_id = models.CharField(
        verbose_name='登録コード',
        max_length=6,
        validators=[verbose_id_validator],
        unique=True,
        help_text='Ex: xA-000'
    )

    kind = models.ForeignKey(
        'project.Kind',
        verbose_name='企画種別',
        on_delete=models.CASCADE,
    )

    food = models.BooleanField(
        verbose_name='飲食物を提供する',
        default=False,
        help_text='1 ユーザーにつき、参加できる飲食物提供企画は 1 企画までです'
    )

    group = models.CharField(
        verbose_name='団体名',
        max_length=50
    )

    group_kana = models.CharField(
        verbose_name='団体名（かな）',
        max_length=50,
        validators=[validators.kana_validator]
    )

    note = models.TextField(
        verbose_name='企画概要・備考',
        help_text='暫定の内容で構いません'
    )

    create_datetime = models.DateTimeField(
        verbose_name='作成日時',
        auto_now_add=True
    )

    class StatusChoice(models.TextChoices):
        WAITING = 'waiting', '待機'
        CALLED = 'called', '対応中'
        PENDING = 'pending', '保留'
        ACCEPTED = 'accepted', '受理'
        REFUSED = 'refused', '却下'

    status = models.CharField(
        verbose_name='状態',
        max_length=10,
        choices=StatusChoice.choices,
        default=StatusChoice.WAITING
    )

    call_id = models.IntegerField(
        verbose_name='整理番号'
    )

    finish_datetime = models.DateTimeField(
        verbose_name='対応終了日時',
        null=True, blank=True
    )

    finish_staff = models.ForeignKey(
        'home.User',
        verbose_name='対応スタッフ',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    leader_token = models.UUIDField(
        verbose_name='企画責任者確定トークン',
        default=uuid.uuid4,
        editable=False
    )


class Window(models.Model):
    class Meta():
        verbose_name = '窓口'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        verbose_name='名前',
        max_length=10
    )

    kind_list = models.ManyToManyField(
        'project.Kind',
        verbose_name='企画種別'
    )

    staff = models.ForeignKey(
        'home.User',
        verbose_name='スタッフ',
        on_delete=models.CASCADE
    )

    registration = models.ForeignKey(
        'register.Registration',
        verbose_name='企画登録',
        on_delete=models.SET_NULL,
        null=True, blank=True
    )


class VerifyToken(models.Model):
    class Meta():
        verbose_name = '企画登録トークン'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id)

    def save(self, **kwargs):
        # Singletone Model
        VerifyToken.objects.all().delete()
        super().save(**kwargs)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    create_datetime = models.DateTimeField(
        verbose_name='作成日時',
        auto_now_add=True
    )


class VerifiedUser(models.Model):
    class Meta():
        verbose_name = '企画登録可能ユーザー'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.user)

    def save(self, **kwargs):
        # すでに同じユーザーの VerifiedUser が存在する場合は削除
        VerifiedUser.objects.filter(user=self.user).delete()
        super().save(**kwargs)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.OneToOneField(
        'home.User',
        verbose_name='ユーザー',
        on_delete=models.CASCADE
    )

    create_datetime = models.DateTimeField(
        verbose_name='作成日時',
        auto_now_add=True
    )


class RegisterStaffManager(models.Manager):
    def check_perm(self, user):
        """あるユーザーが企画登録担当スタッフかどうかを判定

        Args:
            user(User): ユーザー
        Returns:
            bool: 担当スタッフなら Ture (システム管理者も True)
        """
        return user.is_authenticated and (
            RegisterStaff.objects.filter(user=user).exists() or user.is_admin
        )

    def get_user_list(self):
        """統一テーマ管理スタッフを全て求める

        Returns:
            queryset<User>: 統一テーマ管理スタッフのクエリセット
        """
        return User.objects.filter(themestaff__isnull=False)


class RegisterStaff(models.Model):
    class Meta:
        verbose_name = '企画登録担当スタッフ'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.get_full_name()

    objects = RegisterStaffManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user = models.OneToOneField(
        'home.User',
        verbose_name='ユーザー',
        on_delete=models.CASCADE
    )


class RegisterSlack(models.Model):
    class Meta:
        verbose_name = '企画登録slack'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.slack_ch

    def verbose_slack_ch(self):
        """slack_ch を # つきで表示

        Returns:
            str: #channel
        """
        return '#{0}'.format(self.slack_ch)

    def save(self, **kwargs):
        """このインスタンスはたかだか 1 件のみ存在

        セーブ前に必ず全削除する
        """
        # インスタンス全削除
        RegisterSlack.objects.all().delete()
        super().save(**kwargs)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    slack_ch = models.CharField(
        verbose_name='Slack_ch',
        max_length=50,
        help_text='# は除いて登録してください'
    )
