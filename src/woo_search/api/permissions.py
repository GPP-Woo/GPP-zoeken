from __future__ import annotations

from rest_framework.permissions import SAFE_METHODS, BasePermission

from .constants import PermissionOptions
from .models import Application


class TokenAuthPermission(BasePermission):
    def has_permission(self, request, view) -> bool:
        token = request.auth

        if not isinstance(token, Application):
            return False

        assert isinstance(token.permissions, list)

        if (
            request.method in SAFE_METHODS
            and PermissionOptions.read in token.permissions
        ):
            return True

        if (
            request.method not in SAFE_METHODS
            and PermissionOptions.write in token.permissions
        ):
            return True

        return False
