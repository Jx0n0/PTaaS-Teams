from django.db.models import Count, Q
from django.http import FileResponse, Http404
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from business.models import Asset, Batch, Customer, Project, Report, ReportTemplate
from business.permissions import IsAdminOrPMWriteElseReadOnly, IsPMOnlyForReportGenerate
from business.serializers import (
    AssetSerializer,
    BatchSerializer,
    CustomerDetailSerializer,
    CustomerSerializer,
    ProjectSerializer,
    ReportGenerateSerializer,
    ReportSerializer,
    ReportTemplateSerializer,
)
from common.api_permissions import IsScopedObjectAccessible
from common.permissions import ScopeService


class ScopedModelViewSet(ModelViewSet):
    permission_classes = [IsScopedObjectAccessible]

    def get_queryset(self):
        return ScopeService.filter_queryset(self.request.user, super().get_queryset())


class CustomerViewSet(ScopedModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminOrPMWriteElseReadOnly, IsScopedObjectAccessible]

    def get_queryset(self):
        qs = super().get_queryset().annotate(project_count=Count('projects', distinct=True))
        status = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        if status:
            qs = qs.filter(status=status)
        if search:
            qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))
        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CustomerDetailSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.project_count = instance.projects.count()
        instance.report_count = instance.reports.count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class ProjectViewSet(ScopedModelViewSet):
    queryset = Project.objects.select_related('customer').all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAdminOrPMWriteElseReadOnly, IsScopedObjectAccessible]

    def get_queryset(self):
        qs = super().get_queryset().annotate(
            asset_count=Count('assets', distinct=True),
            batch_count=Count('assets__batches', distinct=True),
        )
        customer_id = self.request.query_params.get('customer_id')
        status = self.request.query_params.get('status')
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        if status:
            qs = qs.filter(status=status)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AssetViewSet(ScopedModelViewSet):
    queryset = Asset.objects.select_related('project', 'project__customer').all()
    serializer_class = AssetSerializer


class BatchViewSet(ScopedModelViewSet):
    queryset = Batch.objects.select_related('asset', 'asset__project', 'created_by').all()
    serializer_class = BatchSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ReportTemplateViewSet(ScopedModelViewSet):
    queryset = ReportTemplate.objects.select_related('customer', 'created_by').all()
    serializer_class = ReportTemplateSerializer
    permission_classes = [IsAdminOrPMWriteElseReadOnly, IsScopedObjectAccessible]

    def get_queryset(self):
        qs = super().get_queryset()
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        return qs

    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        if not file:
            raise PermissionDenied('file is required')
        serializer.save(
            created_by=self.request.user,
            file_name=file.name,
            storage_key=f"minio/report-templates/{file.name}",
        )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        obj = self.get_object()
        if not obj.file:
            raise Http404('Template file not found')
        return FileResponse(obj.file.open('rb'), as_attachment=True, filename=obj.file_name)


class ReportViewSet(ScopedModelViewSet):
    queryset = Report.objects.select_related('customer', 'project', 'asset', 'batch', 'template', 'created_by').all()
    serializer_class = ReportSerializer
    permission_classes = [IsAdminOrPMWriteElseReadOnly, IsScopedObjectAccessible]

    def get_queryset(self):
        qs = super().get_queryset()
        if customer_id := self.request.query_params.get('customer_id'):
            qs = qs.filter(customer_id=customer_id)
        if project_id := self.request.query_params.get('project_id'):
            qs = qs.filter(project_id=project_id)
        if status := self.request.query_params.get('status'):
            qs = qs.filter(status=status)
        return qs

    @action(detail=False, methods=['post'], permission_classes=[IsPMOnlyForReportGenerate])
    def generate(self, request):
        serializer = ReportGenerateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        report = Report.objects.create(
            customer_id=data['customer_id'],
            project_id=data['project_id'],
            asset_id=data.get('asset_id'),
            batch_id=data.get('batch_id'),
            template_id=data['template_id'],
            name=data.get('name') or 'Generated Report',
            status=Report.Status.READY,
            generated_file_key='generated/reports/demo.docx',
            created_by=request.user,
        )
        return Response(ReportSerializer(report).data)

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        obj = self.get_object()
        if obj.generated_file:
            return FileResponse(obj.generated_file.open('rb'), as_attachment=True, filename=f'{obj.name}.docx')
        raise Http404('Generated report file not found')
