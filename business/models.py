import uuid

from django.conf import settings
from django.db import models

from common.models import TimeStampedModel


class Customer(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

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
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Project(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class TestType(models.TextChoices):
        WEB = 'web', 'Web'
        APP = 'app', 'App'
        API = 'api', 'API'
        INTERNAL = 'internal', 'Internal'
        EXTERNAL = 'external', 'External'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        IN_REVIEW = 'in_review', 'In Review'
        CLOSED = 'closed', 'Closed'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='projects')
    code = models.SlugField(max_length=50)
    name = models.CharField(max_length=200)
    test_type = models.CharField(max_length=20, choices=TestType.choices, default=TestType.WEB)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    project_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_projects',
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [models.UniqueConstraint(fields=['customer', 'code'], name='uniq_project_code_per_customer')]
        indexes = [models.Index(fields=['customer', 'status', 'test_type'])]

    def __str__(self):
        return f'{self.customer.code}/{self.code}'


class ProjectMember(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class MemberType(models.TextChoices):
        PM = 'PM', 'Project Manager'
        TESTER = 'TESTER', 'Tester'
        QA = 'QA', 'QA'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_memberships')
    member_type = models.CharField(max_length=20, choices=MemberType.choices)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['project', 'user', 'member_type'], name='uniq_project_member_type'),
        ]


class Asset(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class AssetType(models.TextChoices):
        HOST = 'host', 'Host'
        DOMAIN = 'domain', 'Domain'
        URL = 'url', 'URL'
        APP = 'app', 'App'
        API = 'api', 'API'

    class Environment(models.TextChoices):
        PROD = 'prod', 'Production'
        TEST = 'test', 'Test'
        UAT = 'uat', 'UAT'

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assets')
    asset_type = models.CharField(max_length=20, choices=AssetType.choices)
    name = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    fqdn = models.CharField(max_length=255, blank=True)
    url = models.URLField(blank=True)
    environment = models.CharField(max_length=20, choices=Environment.choices, default=Environment.TEST)
    owner = models.CharField(max_length=120, blank=True)
    tags_json = models.JSONField(default=list, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [models.UniqueConstraint(fields=['project', 'name'], name='uniq_asset_name_per_project')]
        indexes = [models.Index(fields=['project', 'asset_type', 'environment'])]

    def __str__(self):
        return self.name


class Batch(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

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
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ReportTemplate(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='report_templates')
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=50, default='v1')
    file_name = models.CharField(max_length=255)
    storage_key = models.CharField(max_length=500)
    file = models.FileField(upload_to='report_templates/')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)


class Report(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

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
