from rest_framework.permissions import BasePermission

from users.models import UserRole


class IsPlatformAdmin(BasePermission):
    """API-level platform admin permission (not dependent on Django admin site)."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return UserRole.objects.filter(user=user, role__code='admin').exists()
