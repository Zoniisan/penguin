import datetime
import uuid

from django.db import models


class ThemeManager(models.Manager):
    def can_submit_check(self, user):
        """統一テーマ案を提出できるかどうかをチェック

        提出済みでなければ True とする
        Args:
            user(User): チェックしたいユーザー
        Returns:
            bool: 提出可能であれば True
        """
        return (
            user.is_authenticated
        ) and (
            not Theme.objects.filter(writer=user).exists()
        )


class Theme(models.Model):
    class Meta:
        verbose_name = '統一テーマ案'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.theme

    objects = ThemeManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    theme = models.CharField(
        verbose_name='統一テーマ案',
        max_length=50,
        help_text='50文字以内で入力してください'
    )

    description = models.CharField(
        verbose_name='趣意文',
        max_length=400,
        help_text='400文字以内で入力してください'
    )

    writer = models.OneToOneField(
        'home.User',
        verbose_name='投稿者',
        on_delete=models.CASCADE
    )

    create_datetime = models.DateTimeField(
        verbose_name='投稿日時',
        auto_now_add=True
    )


class SubmitScheduleManager(models.Manager):
    def is_active(self):
        """提出期間内かどうかを判定

        Returns:
            bool: 提出期間内なら True
        """
        try:
            obj = SubmitSchedule.objects.get()
        except SubmitSchedule.DoesNotExist:
            # そもそもオブジェクトが存在しない場合は提出期間外
            return False

        # 現在日時
        now = datetime.datetime.now()

        return obj.start_datetime <= now and obj.finish_datetime >= now


class SubmitSchedule(models.Model):
    class Meta:
        verbose_name = '提出期間'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '提出期間'

    def save(self, **kwargs):
        """このインスタンスはたかだか 1 件のみ存在

        セーブ前に必ず全削除する
        """
        # インスタンス全削除
        SubmitSchedule.objects.all().delete()
        super().save(**kwargs)

    objects = SubmitScheduleManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    start_datetime = models.DateTimeField(
        verbose_name='開始日時'
    )

    finish_datetime = models.DateTimeField(
        verbose_name='終了日時'
    )


class VoteSchedule(models.Model):
    class Meta:
        verbose_name = '投票期間'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def is_active(self):
        """投票期間内かどうかを判定

        Returns:
            bool: 投票期間内なら True
        """
        now = datetime.datetime.now()
        return self.start_datetime <= now and self.finish_datetime >= now

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        verbose_name='名前',
        max_length=50
    )

    start_datetime = models.DateTimeField(
        verbose_name='開始日時'
    )

    finish_datetime = models.DateTimeField(
        verbose_name='終了日時'
    )


class Vote(models.Model):
    class Meta:
        verbose_name = '投票'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.theme.theme

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    schedule = models.ForeignKey(
        'theme.VoteSchedule',
        verbose_name='投票期間',
        on_delete=models.CASCADE
    )

    theme = models.ForeignKey(
        'theme.Theme',
        verbose_name='統一テーマ案',
        on_delete=models.CASCADE
    )

    create_datetime = models.DateTimeField(
        verbose_name='投票日時',
        auto_now_add=True
    )


class EptidManager(models.Manager):
    def can_vote(self, schedule, user):
        """投票できるかどうかを判定

        投票済みでなければ True

        Args:
            schedule(VoteSchedule): 投票期間
            user(User): ユーザー
        Returns:
            bool: 投票可能なら True
        """
        return user.is_authenticated and not Eptid.obejcts.filter(
            schedule=schedule, eptid=user.eptid
        ).exists()


class Eptid(models.Model):
    class Meta:
        verbose_name = 'eptid'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.eptid

    objects = EptidManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    schedule = models.ForeignKey(
        'theme.VoteSchedule',
        verbose_name='投票期間',
        on_delete=models.CASCADE
    )

    eptid = models.CharField(
        verbose_name='eptid',
        max_length=200
    )


class ThemeStaffManager(models.Manager):
    def theme_staff_check(user):
        """あるユーザーが統一テーマ担当スタッフかどうかを判定

        Args:
            user(User): ユーザー
        Returns:
            bool: 担当スタッフなら Ture
        """
        return user.is_authenticated \
            and ThemeStaff.objects.filter(user=user).exists()


class ThemeStaff(models.Model):
    class Meta:
        verbose_name = '統一テーマ担当スタッフ'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.eptid

    objects = ThemeStaffManager()

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
