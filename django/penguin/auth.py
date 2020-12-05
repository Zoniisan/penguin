from django.contrib.auth.backends import BaseBackend
from home.models import User
from rest_framework import permissions


class NoPasswordBackend(BaseBackend):
    """local 環境専用の認証バックエンド

    パスワードを必要とせず、eptid が一致すれば認証する。
    ただし、is_active = False の場合は認証しない。
    """
    def authenticate(self, request, eptid=None):
        try:
            user = User.objects.get(eptid=eptid)
            if user.is_active:
                return user
            else:
                return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None


class IsAdminPermission(permissions.BasePermission):
    """[REST framework] システム管理者専用

    システム管理者以外アクセスできない ViewSet はこれを利用すること
    """
    message = 'システム管理者以外アクセスできません。'

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin
