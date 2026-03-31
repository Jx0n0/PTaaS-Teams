from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from business.models import Asset, Batch, Customer, Project
from business.serializers import AssetSerializer, BatchSerializer, CustomerSerializer, ProjectSerializer
from common.api_permissions import IsScopedObjectAccessible
from common.permissions import ScopeService


class ScopedModelViewSet(ModelViewSet):
    permission_classes = [IsScopedObjectAccessible]

    def get_queryset(self):
        return ScopeService.filter_queryset(self.request.user, super().get_queryset())


class CustomerViewSet(ScopedModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def perform_create(self, serializer):
        if not ScopeService.can_manage_customer_project(self.request.user):
            raise PermissionDenied('Only PM/Admin can create customers.')
        serializer.save()

    def perform_update(self, serializer):
        if not ScopeService.can_manage_customer_project(self.request.user):
            raise PermissionDenied('Only PM/Admin can update customers.')
        serializer.save()

    def perform_destroy(self, instance):
        if not ScopeService.can_manage_customer_project(self.request.user):
            raise PermissionDenied('Only PM/Admin can delete customers.')
        instance.delete()


class ProjectViewSet(ScopedModelViewSet):
    queryset = Project.objects.select_related('customer').all()
    serializer_class = ProjectSerializer

    def perform_create(self, serializer):
        if not ScopeService.can_manage_customer_project(self.request.user):
            raise PermissionDenied('Only PM/Admin can create projects.')
        serializer.save()

    def perform_update(self, serializer):
        if not ScopeService.can_manage_customer_project(self.request.user):
            raise PermissionDenied('Only PM/Admin can update projects.')
        serializer.save()

    def perform_destroy(self, instance):
        if not ScopeService.can_manage_customer_project(self.request.user):
            raise PermissionDenied('Only PM/Admin can delete projects.')
        instance.delete()


class AssetViewSet(ScopedModelViewSet):
    queryset = Asset.objects.select_related('project', 'project__customer').all()
    serializer_class = AssetSerializer

    def perform_create(self, serializer):
        if not ScopeService.can_manage_asset_batch(self.request.user):
            raise PermissionDenied('Only Tester/PM/Admin can create assets.')
        serializer.save()

    def perform_update(self, serializer):
        if not ScopeService.can_manage_asset_batch(self.request.user):
            raise PermissionDenied('Only Tester/PM/Admin can update assets.')
        serializer.save()

    def perform_destroy(self, instance):
        if not ScopeService.can_manage_asset_batch(self.request.user):
            raise PermissionDenied('Only Tester/PM/Admin can delete assets.')
        instance.delete()


class BatchViewSet(ScopedModelViewSet):
    queryset = Batch.objects.select_related('asset', 'asset__project', 'created_by').all()
    serializer_class = BatchSerializer

    def perform_create(self, serializer):
        if not ScopeService.can_manage_asset_batch(self.request.user):
            raise PermissionDenied('Only Tester/PM/Admin can create batches.')
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        if not ScopeService.can_manage_asset_batch(self.request.user):
            raise PermissionDenied('Only Tester/PM/Admin can update batches.')
        serializer.save()

    def perform_destroy(self, instance):
        if not ScopeService.can_manage_asset_batch(self.request.user):
            raise PermissionDenied('Only Tester/PM/Admin can delete batches.')
        instance.delete()
