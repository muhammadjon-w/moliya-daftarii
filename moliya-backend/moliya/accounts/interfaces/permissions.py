from rest_framework.permissions import BasePermission

from moliya.accounts.interfaces.authentication import AuthenticatedAccount


class IsTelegramAccount(BasePermission):
    message = "Ilovani Telegram ichidan oching."

    def has_permission(self, request, view):
        return isinstance(request.user, AuthenticatedAccount)
