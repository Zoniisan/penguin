import datetime
import uuid

from django.core.validators import RegexValidator
from django.db import IntegrityError, models, transaction
from home.models import User
from penguin import validators


class RegistrationManager(models.Manager):
    def get_call_id_list(self, temp_leader, status):
        """指定したユーザーが仮企画責任者で、かつ指定した状態の
        企画登録情報について、整理番号のリストを取得

        Args:
            temp_leader(User): 仮企画責任者
            status(str): 状態
        Returns:
            list<int>: 整理番号のリスト
        """
        if temp_leader.is_authenticated:
            return Registration.objects.filter(
                temp_leader=temp_leader, status=status
            ).order_by('call_id').values_list('call_id', flat=True)
        else:
            # そもそも認証されていない場合は空リストを返す
            return list()


class Registration(models.Model):
    class Meta():
        verbose_name = '企画登録'
        verbose_name_plural = verbose_name

    def __str__(self):
        if self.verbose_id:
            return '{0}: {1}'.format(self.verbose_id, self.group)
        else:
            return self.group

    def call(self, window_id):
        """状態を「対応中」にする

        Args:
            window_id(uuid): 窓口の ID
        """
        # ID から窓口を取得
        window = Window.objects.get(id=window_id)

        with transaction.atomic():
            # 状態更新
            self.status = 'called'
            self.save()
            # 窓口に企画を紐付ける
            window.registration = self
            window.save()

    def suspend(self):
        """状態を「保留」にする
        """
        # 企画に紐付けられている窓口を取得
        window = Window.objects.get(registration=self)

        with transaction.atomic():
            # 状態更新
            self.status = 'pending'
            self.save()
            # 窓口に紐付けられている企画を解除
            window.registration = None
            window.save()

    def accept(self, staff):
        """状態を「受理」にする

        Args:
            staff(User): 受理スタッフ
        """
        # 企画に紐付けられている窓口を取得
        window = Window.objects.get(registration=self)

        with transaction.atomic():
            # 状態更新
            self.status = 'accept'
            self.finish_staff = staff
            self.finish_datetime = datetime.datetime.now()
            self.save()
            # 窓口に紐付けられている企画を解除
            window.registration = None
            window.save()

    def refuse(self, staff):
        """状態を「却下」にする

        Args:
            staff(User): 却下スタッフ
        """
        # 企画に紐付けられている窓口を取得
        window = Window.objects.get(registration=self)

        with transaction.atomic():
            # 状態更新
            self.status = 'refused'
            self.finish_staff = staff
            self.finish_datetime = datetime.datetime.now()
            self.save()
            # 窓口に紐付けられている状態を解除
            window.registration = None
            window.save()

    def set_verbose_id(self, retry_number=None):
        """登録コードを設定

        通常は引数なしで呼び出すこと
        """
        # 同一企画種別の登録件数（登録コードあり）を取得
        try_number = retry_number if retry_number else\
            Registration.objects.filter(
                kind=self.kind, verbose_id__isnull=False).count()

        try:
            self.verbose_id \
                = 'x{0}-{1}'.format(self.kind.symbol, str(try_number).zfill(3))
            self.save()
        except IntegrityError:
            # すでに同一登録コードのインスタンスが存在する場合
            # 数字を 1 増してリトライ
            self.set_verbose_id(try_number + 1)

    def set_call_id(self, retry_number=None):
        """整理番号を設定

        通常は引数なしで呼び出すこと
        """
        # 企画登録件数を取得
        try_number = retry_number if retry_number else\
            Registration.objects.all().count()

        try:
            self.call_id = try_number
            self.save()
        except IntegrityError:
            # すでに同一整理番号のインスタンスが存在する場合
            # 数字を 1 増してリトライ
            self.set_call_id(try_number + 1)

    objects = RegistrationManager()

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
        help_text='Ex: xA-000',
        null=True
    )

    temp_leader = models.ForeignKey(
        'home.User',
        verbose_name='仮企画責任者',
        on_delete=models.CASCADE,
        related_name='registration_temp_leader'
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
        verbose_name='整理番号',
        unique=True, null=True
    )

    finish_datetime = models.DateTimeField(
        verbose_name='対応終了日時',
        null=True, blank=True
    )

    finish_staff = models.ForeignKey(
        'home.User',
        verbose_name='対応スタッフ',
        related_name='registration_finish_staff',
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
        max_length=10,
        help_text='Ex.「模擬1」「一般2」 案内表示画面には名前順に窓口が表示されます'
    )

    kind_list = models.ManyToManyField(
        'project.Kind',
        verbose_name='対応する企画種別'
    )

    staff = models.OneToOneField(
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


class VerifiedUserManager(models.Manager):
    def check_user(self, user):
        """あるユーザーが企画登録可能ユーザーかどうかを確認する

        Args:
            user(User): ユーザー
        Returns:
            bool: 企画登録可能なら True
        """
        return user.is_authenticated and (
            VerifiedUser.objects.filter(user=user).exists()
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

    objects = VerifiedUserManager()

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
