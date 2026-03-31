from django.contrib import admin

from business.models import Asset, Batch, Customer, Finding, HistoryFinding, Project, ProjectMember, Report, ReportTemplate, ScanFile

admin.site.register(Customer)
admin.site.register(Project)
admin.site.register(ProjectMember)
admin.site.register(Asset)
admin.site.register(Batch)
admin.site.register(ScanFile)
admin.site.register(Finding)
admin.site.register(HistoryFinding)
admin.site.register(ReportTemplate)
admin.site.register(Report)
