from rest_framework.permissions import BasePermission

from common.permissions import ScopeService


class IsScopedObjectAccessible(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return ScopeService.can_access_obj(request.user, obj)
