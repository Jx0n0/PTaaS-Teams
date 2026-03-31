from django.db.models import Count, Exists, OuterRef, Q
from django.http import FileResponse, Http404
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from business.models import Asset, Batch, Customer, Project, ProjectMember, Report, ReportTemplate
from business.permissions import IsAdminOrPMWriteElseReadOnly, IsPMOnlyForReportGenerate, IsProjectAssetWriteAllowed
from business.serializers import (
    AssetDetailSerializer,
    AssetListSerializer,
    AssetWriteSerializer,
    BatchSerializer,
    CustomerDetailSerializer,
    CustomerSerializer,
    ProjectDetailSerializer,
    ProjectListSerializer,
    ProjectWriteSerializer,
    ReportGenerateSerializer,
    ReportSerializer,
    ReportTemplateSerializer,
)
from common.api_permissions import IsScopedObjectAccessible
from common.permissions import ScopeService
from users.models import UserRole


class ScopedModelViewSet(ModelViewSet):
    permission_classes = [IsScopedObjectAccessible]

    def get_queryset(self):
        return ScopeService.filter_queryset(self.request.user, super().get_queryset())


def visible_projects_queryset(user):
    qs = Project.objects.select_related('customer', 'project_manager', 'created_by').prefetch_related('members__user')
    if ScopeService.is_admin(user):
        return qs

    member_sq = ProjectMember.objects.filter(project_id=OuterRef('id'), user=user)
    role_codes = set(UserRole.objects.filter(user=user).values_list('role__code', flat=True))

    scoped_project_ids = ScopeService.project_ids(user)

    if 'PM' in role_codes:
        return qs.filter(Q(project_manager=user) | Exists(member_sq) | Q(id__in=scoped_project_ids)).distinct()

    if 'TESTER' in role_codes or 'QA' in role_codes:
        return qs.filter(Q(id__in=scoped_project_ids) | Exists(member_sq)).distinct()

    return qs.none()


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


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.none()
    permission_classes = [IsAdminOrPMWriteElseReadOnly, IsScopedObjectAccessible]

    def get_queryset(self):
        qs = visible_projects_queryset(self.request.user).annotate(
            asset_count=Count('assets', distinct=True),
            batch_count=Count('assets__batches', distinct=True),
            finding_count=Count('assets__reports', distinct=True),
            open_finding_count=Count('assets__reports', filter=~Q(assets__reports__status=Report.Status.SENT), distinct=True),
        )

        if customer_id := self.request.query_params.get('customer_id'):
            qs = qs.filter(customer_id=customer_id)
        if status := self.request.query_params.get('status'):
            qs = qs.filter(status=status)
        if test_type := self.request.query_params.get('test_type'):
            qs = qs.filter(test_type=test_type)
        if project_manager := self.request.query_params.get('project_manager'):
            qs = qs.filter(project_manager_id=project_manager)
        if search := self.request.query_params.get('search'):
            qs = qs.filter(Q(name__icontains=search) | Q(code__icontains=search))
        return qs.order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        if self.action == 'retrieve':
            return ProjectDetailSerializer
        return ProjectWriteSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], url_path='assets')
    def assets(self, request, pk=None):
        project = self.get_object()
        qs = Asset.objects.filter(project=project).select_related('project', 'project__customer').annotate(
            batch_count=Count('batches', distinct=True),
            finding_count=Count('reports', distinct=True),
        ).order_by('-created_at')
        page = self.paginate_queryset(qs)
        serializer = AssetListSerializer(page if page is not None else qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)


class AssetViewSet(ModelViewSet):
    queryset = Asset.objects.none()
    permission_classes = [IsProjectAssetWriteAllowed, IsScopedObjectAccessible]

    def get_queryset(self):
        project_ids = visible_projects_queryset(self.request.user).values_list('id', flat=True)
        qs = Asset.objects.filter(project_id__in=project_ids).select_related('project', 'project__customer').annotate(
            batch_count=Count('batches', distinct=True),
            finding_count=Count('reports', distinct=True),
            scan_file_count=Count('batches', distinct=True),
            history_finding_count=Count('reports', distinct=True),
        )
        if project_id := self.request.query_params.get('project_id'):
            qs = qs.filter(project_id=project_id)
        if asset_type := self.request.query_params.get('asset_type'):
            qs = qs.filter(asset_type=asset_type)
        if environment := self.request.query_params.get('environment'):
            qs = qs.filter(environment=environment)
        if search := self.request.query_params.get('search'):
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(ip_address__icontains=search)
                | Q(fqdn__icontains=search)
                | Q(url__icontains=search)
            )
        return qs.order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return AssetListSerializer
        if self.action == 'retrieve':
            return AssetDetailSerializer
        return AssetWriteSerializer


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
