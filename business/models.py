from django.conf import settings
from django.db import models

from common.models import TimeStampedModel


class Customer(TimeStampedModel):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Project(TimeStampedModel):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='projects')
    code = models.SlugField(max_length=50)
    name = models.CharField(max_length=200)
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
