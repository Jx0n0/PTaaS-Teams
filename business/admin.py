from django.contrib import admin

from business.models import Asset, Batch, Customer, Project


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'is_active')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'name', 'customer', 'is_active')
    list_filter = ('customer',)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'asset_type', 'project', 'criticality', 'is_active')
    list_filter = ('asset_type', 'project')


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'asset', 'status', 'created_by', 'created_at')
    list_filter = ('status',)
