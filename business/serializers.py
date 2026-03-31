from rest_framework import serializers

from business.models import Asset, Batch, Customer, Project, ProjectMember, Report, ReportTemplate
from users.models import User


class UserSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email']


class CustomerSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'code', 'name', 'status']


class ProjectSummarySerializer(serializers.ModelSerializer):
    customer = CustomerSummarySerializer(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'code', 'name', 'status', 'test_type', 'customer']


class CustomerSerializer(serializers.ModelSerializer):
    project_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'code', 'name', 'status', 'description', 'is_active', 'project_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class CustomerDetailSerializer(CustomerSerializer):
    report_count = serializers.IntegerField(read_only=True)

    class Meta(CustomerSerializer.Meta):
        fields = CustomerSerializer.Meta.fields + ['report_count']


class ProjectMemberSerializer(serializers.ModelSerializer):
    user = UserSummarySerializer(read_only=True)

    class Meta:
        model = ProjectMember
        fields = ['id', 'member_type', 'user', 'created_at']


class ProjectListSerializer(serializers.ModelSerializer):
    customer = CustomerSummarySerializer(read_only=True)
    project_manager = UserSummarySerializer(read_only=True)
    asset_count = serializers.IntegerField(read_only=True)
    batch_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'code', 'customer', 'test_type', 'status',
            'start_date', 'end_date', 'project_manager', 'asset_count', 'batch_count',
        ]


class ProjectDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSummarySerializer(read_only=True)
    project_manager = UserSummarySerializer(read_only=True)
    created_by = UserSummarySerializer(read_only=True)
    asset_count = serializers.IntegerField(read_only=True)
    batch_count = serializers.IntegerField(read_only=True)
    finding_count = serializers.IntegerField(read_only=True)
    open_finding_count = serializers.IntegerField(read_only=True)
    pm_members = serializers.SerializerMethodField()
    tester_members = serializers.SerializerMethodField()
    qa_members = serializers.SerializerMethodField()
    asset_list_entry = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'code', 'customer', 'test_type', 'status', 'description',
            'start_date', 'end_date', 'project_manager', 'created_by',
            'asset_count', 'batch_count', 'finding_count', 'open_finding_count',
            'pm_members', 'tester_members', 'qa_members', 'asset_list_entry',
            'created_at', 'updated_at',
        ]

    def _member_by_type(self, obj, member_type):
        members = [m for m in obj.members.all() if m.member_type == member_type]
        return ProjectMemberSerializer(members, many=True).data

    def get_pm_members(self, obj):
        return self._member_by_type(obj, ProjectMember.MemberType.PM)

    def get_tester_members(self, obj):
        return self._member_by_type(obj, ProjectMember.MemberType.TESTER)

    def get_qa_members(self, obj):
        return self._member_by_type(obj, ProjectMember.MemberType.QA)

    def get_asset_list_entry(self, obj):
        return f'/api/v1/projects/{obj.id}/assets'


class ProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id', 'customer', 'code', 'name', 'test_type', 'status', 'description',
            'start_date', 'end_date', 'project_manager', 'created_by', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']


class AssetListSerializer(serializers.ModelSerializer):
    project = ProjectSummarySerializer(read_only=True)
    batch_count = serializers.IntegerField(read_only=True)
    finding_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'asset_type', 'ip_address', 'fqdn', 'url',
            'environment', 'owner', 'project', 'batch_count', 'finding_count',
        ]


class AssetDetailSerializer(serializers.ModelSerializer):
    project = ProjectSummarySerializer(read_only=True)
    customer = serializers.SerializerMethodField()
    batch_count = serializers.IntegerField(read_only=True)
    scan_file_count = serializers.IntegerField(read_only=True)
    finding_count = serializers.IntegerField(read_only=True)
    history_finding_count = serializers.IntegerField(read_only=True)
    batches = serializers.SerializerMethodField()
    scan_files = serializers.SerializerMethodField()
    findings = serializers.SerializerMethodField()
    history_findings = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            'id', 'project', 'customer', 'asset_type', 'name', 'ip_address', 'fqdn', 'url',
            'environment', 'owner', 'tags_json', 'description',
            'batch_count', 'scan_file_count', 'finding_count', 'history_finding_count',
            'batches', 'scan_files', 'findings', 'history_findings',
            'created_at', 'updated_at',
        ]

    def get_customer(self, obj):
        return CustomerSummarySerializer(obj.project.customer).data

    def get_batches(self, obj):
        return f'/api/v1/batches?asset_id={obj.id}'

    def get_scan_files(self, obj):
        return f'/api/v1/scan-files?asset_id={obj.id}'

    def get_findings(self, obj):
        return f'/api/v1/findings?asset_id={obj.id}'

    def get_history_findings(self, obj):
        return f'/api/v1/history-findings?asset_id={obj.id}'


class AssetWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = [
            'id', 'project', 'asset_type', 'name', 'ip_address', 'fqdn', 'url',
            'environment', 'owner', 'tags_json', 'description', 'is_active',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = [
            'id', 'asset', 'name', 'status', 'scheduled_at', 'started_at', 'finished_at',
            'created_by', 'extra', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = ['id', 'customer', 'name', 'version', 'file_name', 'storage_key', 'file', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at', 'file_name', 'storage_key']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            'id', 'customer', 'project', 'asset', 'batch', 'template', 'name',
            'status', 'generated_file_key', 'generated_file', 'created_by', 'created_at'
        ]
        read_only_fields = ['status', 'generated_file_key', 'generated_file', 'created_by', 'created_at']


class ReportGenerateSerializer(serializers.Serializer):
    customer_id = serializers.UUIDField()
    project_id = serializers.UUIDField()
    asset_id = serializers.UUIDField(required=False, allow_null=True)
    batch_id = serializers.UUIDField(required=False, allow_null=True)
    template_id = serializers.UUIDField()
    name = serializers.CharField(required=False, allow_blank=True)
