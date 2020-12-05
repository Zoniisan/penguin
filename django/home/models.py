import datetime
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from ordered_model.models import OrderedModel
from penguin import validators as va


class UserManager(BaseUserManager):
    def create_user(self, eptid, affiliation='student'):
        user = self.model(
            eptid=eptid,
            affiliation=affiliation
        )
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, eptid, affiliation='student'):
        user = self.model(
            eptid=eptid,
            affiliation=affiliation
        )
        user.is_admin = True
        user.set_unusable_password()
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    class Meta:
        verbose_name = 'ユーザー'
        verbose_name_plural = verbose_name

    USERNAME_FIELD = 'eptid'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['affiliation']

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        """Get Full Name

        同じ企画に参加しているメンバーにはこの形式で表示される。

        Returns:
            str: '(文/B1) ときのそら'
        """
        if self.is_identified:
            return '({0}/{1}) {2}{3}'.format(
                self.faculty, self.grade,
                self.last_name, self.first_name
            )
        else:
            return '（情報未入力）'

    def get_short_name(self):
        """Get Short Name

        単純に氏名を表示する場合に利用。

        Returns:
            str: 'ときのそら'
        """
        if self.is_identified:
            return '{0}{1}'.format(
                self.last_name, self.first_name
            )
        else:
            return '（情報未入力）'

    @property
    def is_identified(self):
        """個人情報の入力有無を確認

        特に、eptid 認証の場合は個人情報を入力しなくても一部機能を利用できる。
        学生番号の入力有無によって個人情報の入力有無を判定する。

        Returns:
            bool: 個人情報入力済みなら True
        """
        return self.stid is not None

    @property
    def is_student(self):
        """学生かどうかを確認

        学生以外（教員など）は大幅に機能を制限する。

        Returns:
            bool: 学生なら True
        """
        return self.affiliation == self.AffiliationChoice.STUDENT

    def department_list(self):
        """所属している部局担当を取得する

        ただしシステム管理者は全ての部局担当に所属するものとする

        Returns:
            list[Department]: 所属している部局担当
        """
        if self.is_admin:
            # システム管理者は全ての部局担当に所属
            return Department.objects.all()
        else:
            return Department.objects.filter(member=self)

    @property
    def is_staff(self):
        """所属している部局担当があれば is_staff = True とする

        Returns:
            bool: 所属している部局担当があれば True
        """
        return bool(self.department_list())

    # 以下 4 メソッドは admin サイト導入に必要なもの
    # Permission は利用しないので、「システム管理者なら True」とする
    def user_has_perm(user, perm, obj):
        """
        A backend can raise `PermissionDenied`
        to short-circuit permission checking.
        """
        return user.is_admin

    def has_perm(self, perm, obj=None):
        """user が permission をもつか？

        Permission は利用しないので「システム管理者なら True」とする
        """

        return self.is_admin

    def has_module_perms(self, app_label):
        """user が module permission をもつか？

        Permission は利用しないので「システム管理者なら True」とする
        """
        return self.is_admin

    @property
    def is_superuser(self):
        """user が Admin サイトで全権を持つか？

        「システム管理者」なら全権を持つ
        """
        return self.is_admin

    objects = UserManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    eptid = models.CharField(
        verbose_name='EPTID',
        max_length=200,
        unique=True
    )

    class AffiliationChoice(models.TextChoices):
        STUDENT = 'student', '学生（student）'
        FACULTY = 'faculty', '教員（faculty）'
        STAFF = 'staff', '事務（staff）'
        MEMBER = 'member', 'その他（member）'

    affiliation = models.CharField(
        max_length=10,
        choices=AffiliationChoice.choices,
        default=AffiliationChoice.STUDENT,
        help_text='Shibboleth の idp から取得した情報です。'
    )

    stid = models.CharField(
        verbose_name='学生番号',
        max_length=10,
        unique=True, null=True,
        validators=[va.stid_validator]
    )

    email = models.EmailField(
        verbose_name='メールアドレス',
        max_length=255,
        unique=True, null=True
    )

    tel = models.CharField(
        verbose_name='電話番号',
        max_length=11,
        unique=True, null=True,
        validators=[va.tel_validator]
    )

    last_name = models.CharField(
        verbose_name='姓',
        max_length=50
    )

    first_name = models.CharField(
        verbose_name='名',
        max_length=50
    )

    last_name_kana = models.CharField(
        verbose_name='姓（かな）',
        max_length=50,
        validators=[va.kana_validator]
    )

    first_name_kana = models.CharField(
        verbose_name='名（かな）',
        max_length=50,
        validators=[va.kana_validator]
    )

    class FacultyChoice(models.TextChoices):
        HUMAN = '総', '総合人間学部 / 人間・環境学研究科'
        LETTER = '文', '文学部 / 文学研究科'
        PEDAGOGY = '教', '教育学部 / 教育学研究科'
        JURISPRUDENCE = '法', '法学部 / 法学研究科'
        ECONOMICS = '経', '経済学部 / 経済学研究科'
        SCIENCE = '理', '理学部 / 理学研究科'
        MEDICINE = '医', '医学部 / 医学研究科'
        PHARAMACY = '薬', '薬学部 / 薬学研究科'
        TECHNOROGY = '工', '工学部 / 工学研究科 / 情報学研究科'
        AGRICULTURE = '農', '農学部 / 農学研究科',
        OTHER = '他', 'その他'

    faculty = models.CharField(
        verbose_name='学部・研究科',
        max_length=1,
        choices=FacultyChoice.choices
    )

    class GradeChoice(models.TextChoices):
        BFIRST = 'B1', '学部1回生'
        BSECOND = 'B2', '学部2回生'
        BTHIRD = 'B3', '学部3回生'
        BFORTH = 'B4', '学部4回生'
        BFIFTH = 'B+', '学部5回生以上'
        MASTER = 'Mr', '修士課程'
        DOCTER = 'Dr', '博士課程'
        OTHER = '--', 'その他'

    grade = models.CharField(
        verbose_name='学年',
        max_length=2,
        choices=GradeChoice.choices
    )

    is_active = models.BooleanField(
        verbose_name='有効',
        default=True,
        help_text='BAN する場合はチェックを外します。'
    )

    is_admin = models.BooleanField(
        verbose_name='システム管理者',
        default=False
    )


class IdentifyToken(models.Model):
    class Meta:
        verbose_name = 'ユーザー登録トークン'
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    eptid = models.CharField(
        verbose_name='EPTID',
        max_length=200
    )

    email = models.EmailField(
        verbose_name='メールアドレス',
        max_length=255
    )

    create_datetime = models.DateTimeField(
        verbose_name='登録日時',
        auto_now_add=True
    )

    is_used = models.BooleanField(
        verbose_name='使用済',
        default=False
    )


class Department(OrderedModel):
    class Meta(OrderedModel.Meta):
        verbose_name = '部局担当'
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
        verbose_name='名称',
        max_length=50
    )

    member = models.ManyToManyField(
        'home.User',
        verbose_name='構成員',
        blank=True
    )

    email = models.EmailField(
        verbose_name='メールアドレス',
        max_length=255
    )

    slack_ch = models.CharField(
        verbose_name='slack',
        max_length=50,
        help_text='#は除いて登録してください'
    )


class Notice(models.Model):
    class Meta:
        verbose_name = 'お知らせ'
        verbose_name_plural = verbose_name
        ordering = ('-start_datetime',)

    def __str__(self):
        return self.subject

    def is_active(self):
        """掲載期間内かどうかを判定

        finish_datetime が None の場合は、掲載期間内とみなす

        Returns:
            bool: 掲載期間内なら True
        """
        return (
            datetime.datetime.now() >= self.start_datetime
        ) and (
            self.finish_datetime is None
            or datetime.datetime.now() <= self.finish_datetime
        )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    subject = models.CharField(
        verbose_name='タイトル',
        max_length=20
    )

    body = models.CharField(
        verbose_name='本文',
        max_length=20
    )

    writer = models.ForeignKey(
        'home.User',
        on_delete=models.CASCADE,
        verbose_name='担当'
    )

    start_datetime = models.DateTimeField(
        verbose_name='開始日時',
        default=datetime.datetime.now
    )

    finish_datetime = models.DateTimeField(
        verbose_name='終了日時',
        null=True, blank=True,
        help_text='空欄にした場合、永久的に公開されます'
    )


class Message(models.Model):
    class Meta():
        verbose_name = 'メッセージ'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

    def __str__(self):
        return self.subject

    def is_read_by(self, user):
        """メッセージがあるユーザーに読まれたかどうかを判定

        Returns:
            bool: 既読なら True
        """
        return MessageRead.objects.filter(
            message=self, user=user
        ).exists()

    def to_summary(self):
        """宛先ユーザーを要約する

        宛先が 1 名 -> （工/B1）ときのそら
        宛先が n>1 名 -> （工/B1）ときのそら 他 (n-1) 名

        Returns:
            str: 上参照
        """
        # 宛先の人数
        to_count = self.to.all().count()
        # 宛先の筆頭（str）
        to_first = str(self.to.all().first())

        if to_count == 1:
            # 宛先が 1 名
            return to_first
        else:
            # 宛先が n>1 名
            return '{0} 他 {1} 名'.format(to_first, to_count - 1)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    subject = models.CharField(
        verbose_name='タイトル',
        max_length=50
    )

    body = models.TextField(
        verbose_name='本文'
    )

    writer = models.ForeignKey(
        'home.User',
        verbose_name='送信者',
        on_delete=models.CASCADE,
        related_name='message_writer'
    )

    to = models.ManyToManyField(
        'home.User',
        verbose_name='宛先',
        related_name='message_to'
    )

    department = models.ForeignKey(
        'home.Department',
        verbose_name='部局担当',
        on_delete=models.CASCADE
    )

    create_datetime = models.DateTimeField(
        verbose_name='送信日時',
        auto_now_add=True
    )


class MessageRead(models.Model):
    class Meta():
        verbose_name = 'メッセージ既読'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{0} / {1}'.format(self.message, self.user)

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    message = models.ForeignKey(
        'home.Message',
        verbose_name='メッセージ',
        on_delete=models.CASCADE
    )

    user = models.ForeignKey(
        'home.User',
        verbose_name='ユーザー',
        on_delete=models.CASCADE
    )

    create_datetime = models.DateTimeField(
        verbose_name='既読日時',
        auto_now_add=True
    )


class Contact(models.Model):
    class Meta():
        verbose_name = 'お問い合わせ'
        verbose_name_plural = verbose_name
        ordering = ('-create_datetime',)

    def __str__(self):
        if len(self.body) > 10:
            # 本文が 10 文字以上 → '冴えない君にラブソン......'
            return '{0}......'.format(self.body[:10])
        else:
            # otherwise → 本文をそのまま返す
            return self.body

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    kind = models.ForeignKey(
        'home.ContactKind',
        verbose_name='お問い合わせ種別',
        on_delete=models.CASCADE,
        related_name='contact'
    )

    body = models.TextField(
        verbose_name='本文'
    )

    writer = models.ForeignKey(
        'home.User',
        verbose_name='送信者',
        on_delete=models.CASCADE
    )

    create_datetime = models.DateTimeField(
        verbose_name='送信時刻',
        auto_now_add=True
    )

    is_finished = models.BooleanField(
        verbose_name='対応完了',
        default=False
    )

    message = models.ManyToManyField(
        'home.Message',
        verbose_name='返信メッセージ'
    )


class ContactKind(OrderedModel):
    class Meta(OrderedModel.Meta):
        verbose_name = 'お問い合わせ種別'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def department_str(self):
        """部局担当名を 1 行で表示

        Returns:
            str: おまつり広場局企画室担当, 会計局
        """
        return ", ".join(self.department.all().values_list('name', flat=True))

    def verbose_slack_ch(self):
        """slack_ch を # つきで表示

        Returns:
            str: #channel
        """
        return '#{0}'.format(self.slack_ch)

    @property
    def is_all_finished(self):
        """全て対応済みかどうかを判定

        Returns:
            与えられたお問い合わせ種別に属するお問い合わせが
            全て対応済みなら True そうでなければ False
        """
        return not bool(Contact.objects.filter(kind=self, is_finished=False))

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        verbose_name='名前',
        max_length=50
    )

    department = models.ManyToManyField(
        'home.Department',
        verbose_name='部局担当',
    )

    slack_ch = models.CharField(
        verbose_name='slack',
        max_length=50,
        help_text='#は除いて登録してください'
    )
