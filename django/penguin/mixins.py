from django.contrib.auth.mixins import UserPassesTestMixin


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
