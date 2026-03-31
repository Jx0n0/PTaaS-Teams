from rest_framework.permissions import BasePermission, IsAuthenticated

from users.models import UserRole


class IsPlatformAdmin(BasePermission):
    """Role-based admin gate for management APIs."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return UserRole.objects.filter(user=user, role__code='ADMIN').exists()


class IsAuthenticatedUser(IsAuthenticated):
    """Semantic alias for endpoints open to any logged-in user."""


class AdminOnlyViewSetMixin:
    permission_classes = [IsPlatformAdmin]
