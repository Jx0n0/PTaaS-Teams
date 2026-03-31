from rest_framework import serializers

from business.models import Asset, Batch, Customer, Project


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'code', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'customer', 'code', 'name', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


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
