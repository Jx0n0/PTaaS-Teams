from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import Role, User, UserRole


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (("Custom", {'fields': ('full_name',)}),)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'is_system')
    search_fields = ('code', 'name')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role', 'scope_type', 'customer', 'project')
    list_filter = ('scope_type', 'role')
