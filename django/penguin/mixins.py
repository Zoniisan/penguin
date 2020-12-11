from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy


class IdentifiedOnlyMixin(UserPassesTestMixin):
    """個人情報入力済専用

    個人情報入力済者専用ページの View クラスはこれを継承すること
    """
    raise_exception = True

    def test_func(self):
        return (
            self.request.user.is_authenticated and
            self.request.user.is_identified
        )


class NotIdentifiedOnlyMixin(UserPassesTestMixin):
    """個人情報未入力専用

    個人情報未入力者専用ページの View クラスはこれを継承すること
    """
    raise_exception = True

    def test_func(self):
        return (
            self.request.user.is_authenticated and
            not self.request.user.is_identified
        )


class RedirectIfNotIdentified(UserPassesTestMixin):
    """個人情報を未入力の場合は入力ページにリダイレクト

    ?next={path} を URL の末尾に入れておき、入力終了後
    {path} にリダイレクトさせる
    """

    def test_func(self):
        return (
            self.request.user.is_authenticated and
            self.request.user.is_identified
        )

    def handle_no_permission(self):
        messages.error(self.request, 'この操作には個人情報の入力が必要です！')

        # リダイレクト先を GET パラメータに仕込んでから
        # ユーザー登録ページへ遷移させる
        return HttpResponseRedirect(
            '{0}?next={1}'.format(
                reverse_lazy('home:auth_identify_token_create'),
                self.request.path
            )
        )


class StaffOnlyMixin(UserPassesTestMixin):
    """スタッフ専用

    スタッフ専用ページの View クラスはこれを継承すること
    """
    raise_exception = True

    def test_func(self):
        return (
            self.request.user.is_authenticated and
            self.request.user.is_staff
        )


class AdminOnlyMixin(UserPassesTestMixin):
    """システム管理者専用

    システム管理者専用ページの View クラスはこれを継承すること
    """
    raise_exception = True

    def test_func(self):
        return (
            self.request.user.is_authenticated and
            self.request.user.is_admin
        )
