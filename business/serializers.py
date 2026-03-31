from rest_framework import serializers

from business.models import Asset, Batch, Customer, Finding, HistoryFinding, Project, ProjectMember, Report, ReportTemplate, ScanFile
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


class AssetSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'name', 'asset_type', 'environment']


class BatchSummarySerializer(serializers.ModelSerializer):
    asset = AssetSummarySerializer(read_only=True)
    class Meta:
        model = Batch
        fields = ['id', 'name', 'batch_no', 'status', 'asset']


class CustomerSerializer(serializers.ModelSerializer):
    project_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'code', 'name', 'status', 'description', 'is_active', 'project_count', 'created_at', 'updated_at']


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
        fields = ['id', 'name', 'code', 'customer', 'test_type', 'status', 'start_date', 'end_date', 'project_manager', 'asset_count', 'batch_count']


class ProjectDetailSerializer(serializers.ModelSerializer):
    customer = CustomerSummarySerializer(read_only=True)
    project_manager = UserSummarySerializer(read_only=True)
    created_by = UserSummarySerializer(read_only=True)
    pm_members = serializers.SerializerMethodField(); tester_members = serializers.SerializerMethodField(); qa_members = serializers.SerializerMethodField()
    asset_list_entry = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = ['id','name','code','customer','test_type','status','description','start_date','end_date','project_manager','created_by','pm_members','tester_members','qa_members','asset_list_entry','created_at','updated_at']
    def _members(self, obj, t): return ProjectMemberSerializer([m for m in obj.members.all() if m.member_type == t], many=True).data
    def get_pm_members(self, obj): return self._members(obj, ProjectMember.MemberType.PM)
    def get_tester_members(self, obj): return self._members(obj, ProjectMember.MemberType.TESTER)
    def get_qa_members(self, obj): return self._members(obj, ProjectMember.MemberType.QA)
    def get_asset_list_entry(self, obj): return f'/api/v1/projects/{obj.id}/assets'


class ProjectWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'customer', 'code', 'name', 'test_type', 'status', 'description', 'start_date', 'end_date', 'project_manager', 'created_by', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'created_at', 'updated_at']


class AssetListSerializer(serializers.ModelSerializer):
    project = ProjectSummarySerializer(read_only=True)
    batch_count = serializers.IntegerField(read_only=True)
    finding_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Asset
        fields = ['id','name','asset_type','ip_address','fqdn','url','environment','owner','project','batch_count','finding_count']


class AssetDetailSerializer(serializers.ModelSerializer):
    project = ProjectSummarySerializer(read_only=True)
    customer = serializers.SerializerMethodField()
    class Meta:
        model = Asset
        fields = ['id','project','customer','asset_type','name','ip_address','fqdn','url','environment','owner','tags_json','description','created_at','updated_at']
    def get_customer(self, obj): return CustomerSummarySerializer(obj.project.customer).data


class AssetWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id','project','asset_type','name','ip_address','fqdn','url','environment','owner','tags_json','description','is_active','created_at','updated_at']
        read_only_fields = ['created_at','updated_at']


class BatchSerializer(serializers.ModelSerializer):
    asset = AssetSummarySerializer(read_only=True)
    asset_id = serializers.IntegerField(write_only=True, required=True)
    scan_file_count = serializers.IntegerField(read_only=True)
    finding_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Batch
        fields = ['id','asset','asset_id','name','batch_no','status','scope_summary','start_date','end_date','created_by','scan_file_count','finding_count','created_at','updated_at']
        read_only_fields = ['created_by','created_at','updated_at']
    def create(self, validated_data):
        asset_id = validated_data.pop('asset_id')
        return Batch.objects.create(asset_id=asset_id, **validated_data)
    def update(self, instance, validated_data):
        validated_data.pop('asset_id', None)
        return super().update(instance, validated_data)


class ScanFileSerializer(serializers.ModelSerializer):
    batch = BatchSummarySerializer(read_only=True)
    batch_id = serializers.IntegerField(write_only=True, required=True)
    uploaded_by = UserSummarySerializer(read_only=True)
    class Meta:
        model = ScanFile
        fields = ['id','batch','batch_id','file_name','file_type','parser_type','storage_key','parse_status','parse_summary','uploaded_by','uploaded_at','parsed_at']
        read_only_fields = ['storage_key','parse_status','parse_summary','uploaded_by','uploaded_at','parsed_at']


class FindingSerializer(serializers.ModelSerializer):
    asset = AssetSummarySerializer(read_only=True)
    batch = BatchSummarySerializer(read_only=True)
    asset_id = serializers.IntegerField(write_only=True, required=True)
    batch_id = serializers.IntegerField(write_only=True, required=True)
    class Meta:
        model = Finding
        fields = ['id','title','severity','status','source_type','finding_type','external_id','host','port','protocol','url','parameter','cve_list','cwe_list','description_html','risk_html','remediation_html','evidence_html','asset','batch','asset_id','batch_id','source_scan_file','updated_at']
    def create(self, validated_data):
        return Finding.objects.create(asset_id=validated_data.pop('asset_id'), batch_id=validated_data.pop('batch_id'), **validated_data)


class HistoryFindingSerializer(serializers.ModelSerializer):
    asset = AssetSummarySerializer(read_only=True)
    batch = BatchSummarySerializer(read_only=True)
    class Meta:
        model = HistoryFinding
        fields = ['id','asset','batch','snapshot_title','snapshot_severity','snapshot_status','snapshot_at']


class ReportTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportTemplate
        fields = ['id', 'customer', 'name', 'version', 'file_name', 'storage_key', 'file', 'created_by', 'created_at']
        read_only_fields = ['created_by', 'created_at', 'file_name', 'storage_key']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'customer', 'project', 'asset', 'batch', 'template', 'name', 'status', 'generated_file_key', 'generated_file', 'created_by', 'created_at']
        read_only_fields = ['status', 'generated_file_key', 'generated_file', 'created_by', 'created_at']


class ReportGenerateSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField(); project_id = serializers.IntegerField(); asset_id = serializers.IntegerField(required=False, allow_null=True); batch_id = serializers.IntegerField(required=False, allow_null=True); template_id = serializers.IntegerField(); name = serializers.CharField(required=False, allow_blank=True)
