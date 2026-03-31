import uuid

from django.conf import settings
from django.db import models

from common.models import TimeStampedModel


class Customer(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        ARCHIVED = 'archived', 'Archived'
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    class Meta: ordering = ['-created_at']


class Project(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    class TestType(models.TextChoices):
        WEB='web','Web'; APP='app','App'; API='api','API'; INTERNAL='internal','Internal'; EXTERNAL='external','External'
    class Status(models.TextChoices):
        DRAFT='draft','Draft'; ACTIVE='active','Active'; IN_REVIEW='in_review','In Review'; CLOSED='closed','Closed'
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='projects')
    code = models.SlugField(max_length=50)
    name = models.CharField(max_length=200)
    test_type = models.CharField(max_length=20, choices=TestType.choices, default=TestType.WEB)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    description = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    project_manager = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='managed_projects')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)
    class Meta:
        ordering=['-created_at']
        constraints=[models.UniqueConstraint(fields=['customer','code'], name='uniq_project_code_per_customer')]
        indexes=[models.Index(fields=['customer','status','test_type'])]


class ProjectMember(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class MemberType(models.TextChoices):
        PM='PM','Project Manager'; TESTER='TESTER','Tester'; QA='QA','QA'
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_memberships')
    member_type = models.CharField(max_length=20, choices=MemberType.choices)
    class Meta:
        ordering=['-created_at']
        constraints=[models.UniqueConstraint(fields=['project','user','member_type'], name='uniq_project_member_type')]


class Asset(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    class AssetType(models.TextChoices):
        HOST='host','Host'; DOMAIN='domain','Domain'; URL='url','URL'; APP='app','App'; API='api','API'
    class Environment(models.TextChoices):
        PROD='prod','Production'; TEST='test','Test'; UAT='uat','UAT'
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
        ordering=['-created_at']
        constraints=[models.UniqueConstraint(fields=['project','name'], name='uniq_asset_name_per_project')]
        indexes=[models.Index(fields=['project','asset_type','environment'])]


class Batch(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    class Status(models.TextChoices):
        DRAFT='draft','Draft'; TESTING='testing','Testing'; QA_REVIEW='qa_review','QA Review'; PM_REVIEW='pm_review','PM Review'; REPORTED='reported','Reported'; CLOSED='closed','Closed'
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='batches')
    name = models.CharField(max_length=200)
    batch_no = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    scope_summary = models.TextField(blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    class Meta:
        ordering=['-created_at']
        constraints=[models.UniqueConstraint(fields=['asset','batch_no'], name='uniq_batch_no_per_asset')]
        indexes=[models.Index(fields=['asset','status','start_date'])]


class ScanFile(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class FileType(models.TextChoices):
        NESSUS='nessus','Nessus'; AWVS='awvs','AWVS'; BURP='burp','Burp XML'
    class ParseStatus(models.TextChoices):
        UPLOADED='uploaded','Uploaded'; PARSING='parsing','Parsing'; PARSED='parsed','Parsed'; FAILED='failed','Failed'
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='scan_files')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20, choices=FileType.choices)
    parser_type = models.CharField(max_length=50, blank=True)
    storage_key = models.CharField(max_length=500)
    parse_status = models.CharField(max_length=20, choices=ParseStatus.choices, default=ParseStatus.UPLOADED)
    parse_summary = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    parsed_at = models.DateTimeField(null=True, blank=True)


class Finding(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class SourceType(models.TextChoices):
        MANUAL='manual','Manual'; NESSUS='nessus','Nessus'; AWVS='awvs','AWVS'; BURP='burp','Burp'
    class Severity(models.TextChoices):
        CRITICAL='critical','Critical'; HIGH='high','High'; MEDIUM='medium','Medium'; LOW='low','Low'; INFO='info','Info'
    class Status(models.TextChoices):
        DRAFT='draft','Draft'; OPEN='open','Open'; FIXED='fixed','Fixed'
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='findings')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='findings')
    source_scan_file = models.ForeignKey(ScanFile, null=True, blank=True, on_delete=models.SET_NULL, related_name='findings')
    source_type = models.CharField(max_length=20, choices=SourceType.choices, default=SourceType.MANUAL)
    title = models.CharField(max_length=255)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    finding_type = models.CharField(max_length=100, blank=True)
    external_id = models.CharField(max_length=120, blank=True)
    host = models.CharField(max_length=255, blank=True)
    port = models.CharField(max_length=50, blank=True)
    protocol = models.CharField(max_length=20, blank=True)
    url = models.URLField(blank=True)
    parameter = models.CharField(max_length=255, blank=True)
    cve_list = models.JSONField(default=list, blank=True)
    cwe_list = models.JSONField(default=list, blank=True)
    description_html = models.TextField(blank=True)
    risk_html = models.TextField(blank=True)
    remediation_html = models.TextField(blank=True)
    evidence_html = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_findings')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='updated_findings')


class HistoryFinding(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='history_findings')
    finding = models.ForeignKey(Finding, on_delete=models.CASCADE, related_name='history_snapshots')
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='history_findings')
    snapshot_title = models.CharField(max_length=255)
    snapshot_severity = models.CharField(max_length=20, choices=Finding.Severity.choices)
    snapshot_status = models.CharField(max_length=20, choices=Finding.Status.choices)
    snapshot_data_json = models.JSONField(default=dict, blank=True)
    snapshot_at = models.DateTimeField(auto_now_add=True)


class ReportTemplate(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='report_templates')
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=50, default='v1')
    file_name = models.CharField(max_length=255)
    storage_key = models.CharField(max_length=500)
    file = models.FileField(upload_to='report_templates/')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)


class Report(TimeStampedModel):
    id = models.BigAutoField(primary_key=True)
    class Status(models.TextChoices):
        DRAFT='draft','Draft'; GENERATING='generating','Generating'; READY='ready','Ready'; SENT='sent','Sent'
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
