from django.contrib import admin

from business.models import Asset, Batch, Customer, Project, ProjectMember, Report, ReportTemplate


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'status', 'is_active')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'customer', 'test_type', 'status', 'project_manager', 'is_active')
    list_filter = ('customer', 'status', 'test_type')


@admin.register(ProjectMember)
class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'user', 'member_type', 'created_at')
    list_filter = ('member_type',)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'asset_type', 'project', 'environment', 'owner', 'is_active')
    list_filter = ('asset_type', 'project', 'environment')


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'asset', 'status', 'created_by', 'created_at')
    list_filter = ('status',)


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'version', 'customer', 'created_by', 'created_at')
    list_filter = ('customer',)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'customer', 'project', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'customer')
