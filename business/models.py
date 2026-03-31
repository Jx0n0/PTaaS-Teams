from django.conf import settings
from django.db import models

from common.models import TimeStampedModel


class Customer(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        ARCHIVED = 'archived', 'Archived'

    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Project(TimeStampedModel):
    class TestType(models.TextChoices):
        WEB = 'web', 'Web'
        APP = 'app', 'App'
        API = 'api', 'API'
        INTERNAL = 'internal', 'Internal'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        CLOSED = 'closed', 'Closed'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='projects')
    code = models.SlugField(max_length=50)
    name = models.CharField(max_length=200)
    test_type = models.CharField(max_length=20, choices=TestType.choices, default=TestType.WEB)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['customer', 'code'], name='uniq_project_code_per_customer')
        ]

    def __str__(self):
        return f'{self.customer.code}/{self.code}'


class Asset(TimeStampedModel):
    class AssetType(models.TextChoices):
        DOMAIN = 'DOMAIN', 'Domain'
        IP = 'IP', 'IP'
        URL = 'URL', 'URL'
        MOBILE = 'MOBILE', 'Mobile'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assets')
    name = models.CharField(max_length=200)
    asset_type = models.CharField(max_length=20, choices=AssetType.choices)
    value = models.CharField(max_length=500)
    criticality = models.PositiveSmallIntegerField(default=3)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Batch(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        RUNNING = 'RUNNING', 'Running'
        DONE = 'DONE', 'Done'
        FAILED = 'FAILED', 'Failed'

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='batches')
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    scheduled_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    extra = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class ReportTemplate(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='report_templates')
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=50, default='v1')
    file_name = models.CharField(max_length=255)
    storage_key = models.CharField(max_length=500)
    file = models.FileField(upload_to='report_templates/')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)


class Report(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        GENERATING = 'generating', 'Generating'
        READY = 'ready', 'Ready'
        SENT = 'sent', 'Sent'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='reports')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='reports')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='reports', null=True, blank=True)
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE, related_name='reports')
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    generated_file_key = models.CharField(max_length=500, blank=True)
    generated_file = models.FileField(upload_to='reports/', null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
