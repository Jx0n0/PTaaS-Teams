from django.db.models import Count, Exists, OuterRef, Q
from django.http import FileResponse, Http404
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from business.models import Asset, Batch, Customer, Finding, HistoryFinding, Project, ProjectMember, Report, ReportTemplate, ScanFile
from business.permissions import IsAdminOrPMWriteElseReadOnly, IsPMOnlyForReportGenerate, IsScopedProjectWritePermission
from business.serializers import (
    AssetDetailSerializer, AssetListSerializer, AssetWriteSerializer,
    BatchSerializer, CustomerDetailSerializer, CustomerSerializer,
    FindingSerializer, HistoryFindingSerializer,
    ProjectDetailSerializer, ProjectListSerializer, ProjectWriteSerializer,
    ReportGenerateSerializer, ReportSerializer, ReportTemplateSerializer,
    ScanFileSerializer,
)
from common.api_permissions import IsScopedObjectAccessible
from common.permissions import ScopeService
from users.models import UserRole


def visible_projects_queryset(user):
    qs = Project.objects.select_related('customer', 'project_manager', 'created_by').prefetch_related('members__user')
    if ScopeService.is_admin(user):
        return qs
    member_sq = ProjectMember.objects.filter(project_id=OuterRef('id'), user=user)
    scoped_project_ids = ScopeService.project_ids(user)
    role_codes = set(UserRole.objects.filter(user=user).values_list('role__code', flat=True))
    if 'PM' in role_codes:
        return qs.filter(Q(project_manager=user) | Exists(member_sq) | Q(id__in=scoped_project_ids)).distinct()
    if 'TESTER' in role_codes or 'QA' in role_codes:
        return qs.filter(Q(id__in=scoped_project_ids) | Exists(member_sq)).distinct()
    return qs.none()


class ScopedProjectQuerysetMixin:
    def visible_project_ids(self):
        return visible_projects_queryset(self.request.user).values_list('id', flat=True)


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all(); serializer_class = CustomerSerializer
    permission_classes = [IsAdminOrPMWriteElseReadOnly, IsScopedObjectAccessible]
    def get_queryset(self):
        qs = ScopeService.filter_queryset(self.request.user, super().get_queryset()).annotate(project_count=Count('projects', distinct=True))
        if s := self.request.query_params.get('status'): qs = qs.filter(status=s)
        if q := self.request.query_params.get('search'): qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q))
        return qs
    def get_serializer_class(self): return CustomerDetailSerializer if self.action == 'retrieve' else super().get_serializer_class()


class ProjectViewSet(ModelViewSet):
    queryset = Project.objects.none(); permission_classes = [IsAdminOrPMWriteElseReadOnly, IsScopedObjectAccessible]
    def get_queryset(self):
        qs = visible_projects_queryset(self.request.user).annotate(asset_count=Count('assets', distinct=True), batch_count=Count('assets__batches', distinct=True), finding_count=Count('assets__findings', distinct=True), open_finding_count=Count('assets__findings', filter=Q(assets__findings__status__in=['draft','open']), distinct=True)).order_by('-created_at')
        for key, field in [('customer_id','customer_id'),('status','status'),('test_type','test_type'),('project_manager','project_manager_id')]:
            if v := self.request.query_params.get(key): qs = qs.filter(**{field: v})
        if q := self.request.query_params.get('search'): qs = qs.filter(Q(name__icontains=q) | Q(code__icontains=q))
        return qs
    def get_serializer_class(self):
        if self.action == 'list': return ProjectListSerializer
        if self.action == 'retrieve': return ProjectDetailSerializer
        return ProjectWriteSerializer
    def perform_create(self, serializer): serializer.save(created_by=self.request.user)


class AssetViewSet(ScopedProjectQuerysetMixin, ModelViewSet):
    queryset = Asset.objects.none(); permission_classes = [IsScopedProjectWritePermission, IsScopedObjectAccessible]
    def get_queryset(self):
        qs = Asset.objects.filter(project_id__in=self.visible_project_ids()).select_related('project', 'project__customer').annotate(batch_count=Count('batches', distinct=True), scan_file_count=Count('batches__scan_files', distinct=True), finding_count=Count('findings', distinct=True), history_finding_count=Count('history_findings', distinct=True)).order_by('-created_at')
        if v := self.request.query_params.get('project_id'): qs = qs.filter(project_id=v)
        if v := self.request.query_params.get('asset_type'): qs = qs.filter(asset_type=v)
        if v := self.request.query_params.get('environment'): qs = qs.filter(environment=v)
        if q := self.request.query_params.get('search'): qs = qs.filter(Q(name__icontains=q) | Q(ip_address__icontains=q) | Q(fqdn__icontains=q) | Q(url__icontains=q))
        return qs
    def get_serializer_class(self):
        if self.action == 'list': return AssetListSerializer
        if self.action == 'retrieve': return AssetDetailSerializer
        return AssetWriteSerializer

    @action(detail=True, methods=['get'], url_path='batches')
    def batches(self, request, pk=None):
        qs = Batch.objects.filter(asset_id=pk, asset__project_id__in=self.visible_project_ids()).select_related('asset').annotate(scan_file_count=Count('scan_files', distinct=True), finding_count=Count('findings', distinct=True)).order_by('-created_at')
        page = self.paginate_queryset(qs); ser = BatchSerializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)

    @action(detail=True, methods=['get'], url_path='findings')
    def findings(self, request, pk=None):
        qs = Finding.objects.filter(asset_id=pk, asset__project_id__in=self.visible_project_ids()).select_related('asset','batch').order_by('-updated_at')
        page = self.paginate_queryset(qs); ser = FindingSerializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)

    @action(detail=True, methods=['get'], url_path='history-findings')
    def history_findings(self, request, pk=None):
        qs = HistoryFinding.objects.filter(asset_id=pk, asset__project_id__in=self.visible_project_ids()).select_related('asset','batch').order_by('-snapshot_at')
        page = self.paginate_queryset(qs); ser = HistoryFindingSerializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)

    @action(detail=False, methods=['get'], url_path=r'projects/(?P<project_id>[^/.]+)/assets')
    def by_project(self, request, project_id=None):
        qs = self.get_queryset().filter(project_id=project_id)
        page = self.paginate_queryset(qs)
        ser = AssetListSerializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)


class BatchViewSet(ScopedProjectQuerysetMixin, ModelViewSet):
    queryset = Batch.objects.none(); serializer_class = BatchSerializer
    permission_classes = [IsScopedProjectWritePermission, IsScopedObjectAccessible]
    def get_queryset(self):
        qs = Batch.objects.filter(asset__project_id__in=self.visible_project_ids()).select_related('asset','asset__project').annotate(scan_file_count=Count('scan_files', distinct=True), finding_count=Count('findings', distinct=True)).order_by('-created_at')
        if v := self.request.query_params.get('asset_id'): qs = qs.filter(asset_id=v)
        if v := self.request.query_params.get('project_id'): qs = qs.filter(asset__project_id=v)
        if v := self.request.query_params.get('status'): qs = qs.filter(status=v)
        if v := self.request.query_params.get('start_date'): qs = qs.filter(start_date__gte=v)
        if v := self.request.query_params.get('end_date'): qs = qs.filter(end_date__lte=v)
        return qs
    def perform_create(self, serializer): serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], url_path='scan-files')
    def scan_files(self, request, pk=None):
        qs = ScanFile.objects.filter(batch_id=pk, batch__asset__project_id__in=self.visible_project_ids()).select_related('batch','uploaded_by').order_by('-uploaded_at')
        page = self.paginate_queryset(qs); ser = ScanFileSerializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)

    @action(detail=True, methods=['get'], url_path='findings')
    def findings(self, request, pk=None):
        qs = Finding.objects.filter(batch_id=pk, asset__project_id__in=self.visible_project_ids()).select_related('asset','batch').order_by('-updated_at')
        page = self.paginate_queryset(qs); ser = FindingSerializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)

    @action(detail=False, methods=['get'], url_path=r'assets/(?P<asset_id>[^/.]+)/batches')
    def by_asset(self, request, asset_id=None):
        qs = self.get_queryset().filter(asset_id=asset_id)
        page = self.paginate_queryset(qs); ser = self.get_serializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)


class ScanFileViewSet(ScopedProjectQuerysetMixin, ModelViewSet):
    queryset = ScanFile.objects.none(); serializer_class = ScanFileSerializer
    permission_classes = [IsScopedProjectWritePermission, IsScopedObjectAccessible]
    http_method_names = ['get', 'post', 'head', 'options']
    def get_queryset(self):
        qs = ScanFile.objects.filter(batch__asset__project_id__in=self.visible_project_ids()).select_related('batch','batch__asset','uploaded_by').order_by('-uploaded_at')
        if v := self.request.query_params.get('batch_id'): qs = qs.filter(batch_id=v)
        if v := self.request.query_params.get('asset_id'): qs = qs.filter(batch__asset_id=v)
        return qs
    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        batch_id = request.data.get('batch_id'); file_type = request.data.get('file_type'); file = request.FILES.get('file')
        if not batch_id or not file_type or not file: raise PermissionDenied('batch_id/file_type/file is required')
        obj = ScanFile.objects.create(batch_id=batch_id, file_name=file.name, file_type=file_type, parser_type=file_type, storage_key=f'minio/scan-files/{batch_id}/{file.name}', parse_status=ScanFile.ParseStatus.UPLOADED, uploaded_by=request.user)
        return Response(ScanFileSerializer(obj).data)
    @action(detail=False, methods=['get'], url_path=r'batches/(?P<batch_id>[^/.]+)/scan-files')
    def by_batch(self, request, batch_id=None):
        qs = self.get_queryset().filter(batch_id=batch_id); page = self.paginate_queryset(qs); ser = self.get_serializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)


class FindingViewSet(ScopedProjectQuerysetMixin, ModelViewSet):
    queryset = Finding.objects.none(); serializer_class = FindingSerializer
    permission_classes = [IsScopedProjectWritePermission, IsScopedObjectAccessible]
    def get_queryset(self):
        qs = Finding.objects.filter(asset__project_id__in=self.visible_project_ids()).select_related('asset','batch','source_scan_file').order_by('-updated_at')
        for p in ['asset_id','batch_id','severity','status','source_type']:
            if v := self.request.query_params.get(p): qs = qs.filter(**{p: v})
        if q := self.request.query_params.get('search'): qs = qs.filter(Q(title__icontains=q) | Q(external_id__icontains=q))
        return qs
    def perform_create(self, serializer):
        finding = serializer.save(created_by=self.request.user, updated_by=self.request.user)
        create_history_snapshot(finding)
    def perform_update(self, serializer):
        finding = serializer.save(updated_by=self.request.user)
        create_history_snapshot(finding)
    @action(detail=False, methods=['get'], url_path=r'assets/(?P<asset_id>[^/.]+)/findings')
    def by_asset(self, request, asset_id=None):
        qs = self.get_queryset().filter(asset_id=asset_id); page = self.paginate_queryset(qs); ser = self.get_serializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)
    @action(detail=False, methods=['get'], url_path=r'batches/(?P<batch_id>[^/.]+)/findings')
    def by_batch(self, request, batch_id=None):
        qs = self.get_queryset().filter(batch_id=batch_id); page = self.paginate_queryset(qs); ser = self.get_serializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)


class HistoryFindingViewSet(ScopedProjectQuerysetMixin, ModelViewSet):
    queryset = HistoryFinding.objects.none(); serializer_class = HistoryFindingSerializer
    permission_classes = [IsScopedProjectWritePermission, IsScopedObjectAccessible]
    http_method_names = ['get', 'head', 'options']
    def get_queryset(self):
        qs = HistoryFinding.objects.filter(asset__project_id__in=self.visible_project_ids()).select_related('asset','batch').order_by('-snapshot_at')
        if v := self.request.query_params.get('asset_id'): qs = qs.filter(asset_id=v)
        if v := self.request.query_params.get('batch_id'): qs = qs.filter(batch_id=v)
        if v := self.request.query_params.get('snapshot_severity'): qs = qs.filter(snapshot_severity=v)
        if v := self.request.query_params.get('snapshot_status'): qs = qs.filter(snapshot_status=v)
        return qs
    @action(detail=False, methods=['get'], url_path=r'assets/(?P<asset_id>[^/.]+)/history-findings')
    def by_asset(self, request, asset_id=None):
        qs = self.get_queryset().filter(asset_id=asset_id); page = self.paginate_queryset(qs); ser = self.get_serializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(ser.data) if page is not None else Response(ser.data)


class ReportTemplateViewSet(ModelViewSet):
    queryset = ReportTemplate.objects.select_related('customer', 'created_by').all(); serializer_class = ReportTemplateSerializer
    permission_classes = [IsAdminOrPMWriteElseReadOnly, IsScopedObjectAccessible]
    def get_queryset(self):
        qs = ScopeService.filter_queryset(self.request.user, super().get_queryset())
        if customer_id := self.request.query_params.get('customer_id'): qs = qs.filter(customer_id=customer_id)
        return qs
    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        if not file: raise PermissionDenied('file is required')
        serializer.save(created_by=self.request.user, file_name=file.name, storage_key=f'minio/report-templates/{file.name}')
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        obj = self.get_object()
        if not obj.file: raise Http404('Template file not found')
        return FileResponse(obj.file.open('rb'), as_attachment=True, filename=obj.file_name)


class ReportViewSet(ModelViewSet):
    queryset = Report.objects.select_related('customer','project','asset','batch','template','created_by').all(); serializer_class = ReportSerializer
    permission_classes = [IsAdminOrPMWriteElseReadOnly, IsScopedObjectAccessible]
    def get_queryset(self):
        qs = ScopeService.filter_queryset(self.request.user, super().get_queryset())
        if v := self.request.query_params.get('customer_id'): qs = qs.filter(customer_id=v)
        if v := self.request.query_params.get('project_id'): qs = qs.filter(project_id=v)
        if v := self.request.query_params.get('status'): qs = qs.filter(status=v)
        return qs
    @action(detail=False, methods=['post'], permission_classes=[IsPMOnlyForReportGenerate])
    def generate(self, request):
        serializer = ReportGenerateSerializer(data=request.data); serializer.is_valid(raise_exception=True); data = serializer.validated_data
        report = Report.objects.create(customer_id=data['customer_id'], project_id=data['project_id'], asset_id=data.get('asset_id'), batch_id=data.get('batch_id'), template_id=data['template_id'], name=data.get('name') or 'Generated Report', status=Report.Status.READY, generated_file_key='generated/reports/demo.docx', created_by=request.user)
        return Response(ReportSerializer(report).data)


def create_history_snapshot(finding):
    HistoryFinding.objects.create(
        asset=finding.asset, finding=finding, batch=finding.batch,
        snapshot_title=finding.title, snapshot_severity=finding.severity, snapshot_status=finding.status,
        snapshot_data_json={'external_id': finding.external_id, 'source_type': finding.source_type},
    )
