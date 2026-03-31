from rest_framework.permissions import BasePermission, SAFE_METHODS

from common.permissions import ScopeService
from users.models import UserRole


class IsAdminOrPMWriteElseReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if user.is_superuser:
            return True
        return UserRole.objects.filter(user=user, role__code__in=['ADMIN', 'PM']).exists()


class IsScopedProjectWritePermission(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        if ScopeService.is_admin(user):
            return True
        return UserRole.objects.filter(user=user, role__code__in=['PM', 'TESTER']).exists()


class IsPMOnlyForReportGenerate(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        return UserRole.objects.filter(user=user, role__code='PM').exists()
