import datetime
import uuid

from django.db import models
from home.models import User


class ThemeManager(models.Manager):
    def can_submit_check(self, user):
        """統一テーマ案を提出できるかどうかをチェック

        正規学生かつ提出済みでなければ True とする
        Args:
            user(User): チェックしたいユーザー
        Returns:
            bool: 提出可能であれば True
        """
        return (
            user.is_authenticated and user.is_identified
            and user.is_student
        ) and (
            not Theme.objects.filter(writer=user).exists()
        )


class Theme(models.Model):
    class Meta:
        verbose_name = '統一テーマ案'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.theme

    def get_count(self, vote_schedule):
        """投票日程ごとに票数を計算

        Args:
            vote_schedule(VoteSchedule): 投票日程
        Returns:
            int: 獲得票数
        """
        return Vote.objects.filter(theme=self, schedule=vote_schedule).count()

    objects = ThemeManager()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    theme = models.CharField(
        verbose_name='統一テーマ案',
        max_length=100,
        help_text='100文字以内で入力してください'
    )

    description = models.CharField(
        verbose_name='趣意文',
        max_length=400,
        help_text='400文字以内で入力してください'
    )

    writer = models.OneToOneField(
        'home.User',
        verbose_name='投稿者',
        on_delete=models.CASCADE,
        related_name='theme_writer'
    )

    create_datetime = models.DateTimeField(
        verbose_name='投稿日時',
        auto_now_add=True
    )

    update_datetime = models.DateTimeField(
        verbose_name='最終編集日時',
        auto_now=True
    )

    submit_staff = models.ForeignKey(
        'home.User',
        verbose_name='強制提出スタッフ',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        help_text='強制提出操作を行った場合、担当したスタッフが記録されます',
        related_name='theme_submit_staff'
    )

    update_staff = models.ForeignKey(
        'home.User',
        verbose_name='最終編集スタッフ',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        help_text='編集操作を行った場合、担当したスタッフが記録されます',
        related_name='theme_update_staff'
    )


class SubmitScheduleManager(models.Manager):
    def is_active(self):
        """提出日程内かどうかを判定

        Returns:
            bool: 提出日程内なら True
        """
        try:
            obj = SubmitSchedule.objects.get()
        except SubmitSchedule.DoesNotExist:
            # そもそもオブジェクトが存在しない場合は提出日程外
            return False

        # 現在日時
        now = datetime.datetime.now()

        return obj.start_datetime <= now and obj.finish_datetime >= now


class SubmitSchedule(models.Model):
    class Meta:
        verbose_name = '提出日程'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '提出日程'

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
        verbose_name = '投票日程'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_status(self):
        """投票日程の状態を判定

        Returns:
            str: 'pending': 開始前, 'active': 投票中, 'finished': 終了
        """
        now = datetime.datetime.now()

        if now < self.start_datetime:
            return 'pending'
        elif self.start_datetime <= now and now <= self.finish_datetime:
            return 'active'
        else:
            return 'finished'

    def is_active(self):
        """投票日程の状態が active かどうかを判定

        Returns:
            bool: active なら True
        """
        return self.get_status() == 'active'

    def can_vote_check(self, user):
        """投票できるかどうかを判定

        正規学生 and 投票済みでなければ True

        Args:
            user(User): ユーザー
        Returns:
            bool: 投票可能なら True
        """
        return user.is_authenticated and user.is_student and \
            not Eptid.objects.filter(
                schedule=self, eptid=user.eptid
            ).exists()

    def get_total_count(self):
        """総得票数をカウントする

        Returns:
            int: 総得票数
        """
        return Vote.objects.filter(schedule=self).count()

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    name = models.CharField(
        verbose_name='名前',
        max_length=50
    )

    description = models.CharField(
        verbose_name='説明文',
        max_length=50, blank=True, null=True
    )

    start_datetime = models.DateTimeField(
        verbose_name='開始日時'
    )

    finish_datetime = models.DateTimeField(
        verbose_name='終了日時'
    )

    theme_list = models.ManyToManyField(
        'theme.Theme',
        verbose_name='統一テーマ案'
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
        verbose_name='投票日程',
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


class Eptid(models.Model):
    class Meta:
        verbose_name = 'eptid'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.eptid

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    schedule = models.ForeignKey(
        'theme.VoteSchedule',
        verbose_name='投票日程',
        on_delete=models.CASCADE
    )

    eptid = models.CharField(
        verbose_name='eptid',
        max_length=200
    )


class ThemeStaffManager(models.Manager):
    def check_perm(self, user):
        """あるユーザーが統一テーマ担当スタッフかどうかを判定

        Args:
            user(User): ユーザー
        Returns:
            bool: 担当スタッフなら Ture (システム管理者も True)
        """
        return user.is_authenticated and (
            ThemeStaff.objects.filter(user=user).exists() or user.is_admin
        )

    def get_user_list(self):
        """統一テーマ管理スタッフを全て求める

        Returns:
            queryset<User>: 統一テーマ管理スタッフのクエリセット
        """
        return User.objects.filter(themestaff__isnull=False)


class ThemeStaff(models.Model):
    class Meta:
        verbose_name = '統一テーマ担当スタッフ'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.get_full_name()

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


class ThemeSlack(models.Model):
    class Meta:
        verbose_name = '統一テーマ案slack'
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
        ThemeSlack.objects.all().delete()
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
