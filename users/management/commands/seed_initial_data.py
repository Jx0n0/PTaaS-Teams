from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from business.models import Asset, Batch, Customer, Project
from users.models import Role, UserRole


class Command(BaseCommand):
    help = 'Seed initial users/roles and business-tree demo data'

    def handle(self, *args, **options):
        User = get_user_model()
        admin_role, _ = Role.objects.get_or_create(code='ADMIN', defaults={'name': 'Admin', 'is_system': True})
        pm_role, _ = Role.objects.get_or_create(code='PM', defaults={'name': 'Project Manager', 'is_system': True})
        tester_role, _ = Role.objects.get_or_create(code='TESTER', defaults={'name': 'Tester', 'is_system': True})
        qa_role, _ = Role.objects.get_or_create(code='QA', defaults={'name': 'QA', 'is_system': True})

        admin, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True})
        admin.set_password('Admin123!')
        admin.save()

        pm, _ = User.objects.get_or_create(username='pm_demo', defaults={'email': 'pm@example.com'})
        pm.set_password('Pm123456!')
        pm.save()

        tester, _ = User.objects.get_or_create(username='tester_demo', defaults={'email': 'tester@example.com'})
        tester.set_password('Tester123!')
        tester.save()

        qa, _ = User.objects.get_or_create(username='qa_demo', defaults={'email': 'qa@example.com'})
        qa.set_password('Qa123456!')
        qa.save()

        customer, _ = Customer.objects.get_or_create(code='acme', defaults={'name': 'ACME Corp'})
        project, _ = Project.objects.get_or_create(customer=customer, code='web-2026', defaults={'name': 'Web Pentest 2026'})
        asset, _ = Asset.objects.get_or_create(project=project, name='Main Domain', defaults={'asset_type': Asset.AssetType.DOMAIN, 'value': 'acme.com'})
        Batch.objects.get_or_create(asset=asset, name='Q1 Full Scan')

        UserRole.objects.get_or_create(user=admin, role=admin_role, scope_type=UserRole.ScopeType.GLOBAL)
        UserRole.objects.get_or_create(user=pm, role=pm_role, scope_type=UserRole.ScopeType.PROJECT, project=project)
        UserRole.objects.get_or_create(user=tester, role=tester_role, scope_type=UserRole.ScopeType.PROJECT, project=project)
        UserRole.objects.get_or_create(user=qa, role=qa_role, scope_type=UserRole.ScopeType.PROJECT, project=project)

        self.stdout.write(self.style.SUCCESS('Seed data created/updated successfully.'))
