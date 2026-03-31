from rest_framework import serializers

from business.models import Asset, Batch, Customer, Project, Report, ReportTemplate


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


class ProjectSerializer(serializers.ModelSerializer):
    asset_count = serializers.IntegerField(read_only=True)
    batch_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'customer', 'code', 'name', 'test_type', 'status', 'description',
            'start_date', 'end_date', 'created_by', 'is_active',
            'asset_count', 'batch_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'project', 'name', 'asset_type', 'value', 'criticality', 'is_active', 'created_at', 'updated_at']
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
    customer_id = serializers.IntegerField()
    project_id = serializers.IntegerField()
    asset_id = serializers.IntegerField(required=False, allow_null=True)
    batch_id = serializers.IntegerField(required=False, allow_null=True)
    template_id = serializers.IntegerField()
    name = serializers.CharField(required=False, allow_blank=True)
