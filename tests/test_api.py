from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import Role, UserRole
from business.models import Asset, Batch, Customer, Finding, HistoryFinding, Project, ProjectMember


class PlatformApiTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            username='platform_admin',
            email='admin@test.com',
            password='Admin123!',
            full_name='Platform Admin',
            is_active=True,
        )
        self.normal_user = User.objects.create_user(
            username='tester',
            email='tester@test.com',
            password='OldPass123!',
            full_name='Demo Tester',
            is_active=True,
        )

        self.admin_role, _ = Role.objects.get_or_create(code='ADMIN', defaults={'name': 'Admin'})
        self.tester_role, _ = Role.objects.get_or_create(code='TESTER', defaults={'name': 'Tester'})
        UserRole.objects.create(user=self.admin_user, role=self.admin_role, scope_type=UserRole.ScopeType.GLOBAL)
        UserRole.objects.create(user=self.normal_user, role=self.tester_role, scope_type=UserRole.ScopeType.GLOBAL)

    def _login(self, username, password):
        return self.client.post('/api/v1/auth/login', {'username': username, 'password': password}, format='json')

    def test_login_returns_tokens_user_and_roles(self):
        resp = self._login('tester', 'OldPass123!')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertEqual(resp.data['user']['username'], 'tester')
        self.assertIn('TESTER', resp.data['roles'])

    def test_me_returns_expected_fields(self):
        login = self._login('tester', 'OldPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        resp = self.client.get('/api/v1/auth/me')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(resp.data.keys()),
            {'id', 'username', 'email', 'full_name', 'is_active', 'roles'},
        )

    def test_change_password_requires_old_password_and_confirmation(self):
        login = self._login('tester', 'OldPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        bad = self.client.post(
            '/api/v1/auth/change-password',
            {'old_password': 'wrong', 'new_password': 'NewPass123!', 'confirm_password': 'NewPass123!'},
            format='json',
        )
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)

        ok = self.client.post(
            '/api/v1/auth/change-password',
            {'old_password': 'OldPass123!', 'new_password': 'NewPass123!', 'confirm_password': 'NewPass123!'},
            format='json',
        )
        self.assertEqual(ok.status_code, status.HTTP_200_OK)

    def test_refresh_token(self):
        login = self._login('tester', 'OldPass123!')
        resp = self.client.post('/api/v1/auth/refresh', {'refresh': login.data['refresh']}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)

    def test_user_role_management_is_api_based_not_django_admin(self):
        login = self._login('platform_admin', 'Admin123!')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        create_user = self.client.post(
            '/api/v1/users',
            {'username': 'pm1', 'email': 'pm1@test.com', 'full_name': 'PM 1', 'password': 'Pm123456!'},
            format='json',
        )
        self.assertEqual(create_user.status_code, status.HTTP_201_CREATED)

        create_role = self.client.post('/api/v1/roles', {'code': 'PM', 'name': 'Project Manager'}, format='json')
        self.assertEqual(create_role.status_code, status.HTTP_201_CREATED)

        bind = self.client.post(
            '/api/v1/user-roles',
            {'user': create_user.data['id'], 'role': create_role.data['id'], 'scope_type': 'GLOBAL'},
            format='json',
        )
        self.assertEqual(bind.status_code, status.HTTP_201_CREATED)

    def test_non_admin_cannot_manage_user_role(self):
        login = self._login('tester', 'OldPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        resp = self.client.get('/api/v1/users')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


    def test_user_list_is_paginated_and_filterable(self):
        login = self._login('platform_admin', 'Admin123!')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        resp = self.client.get('/api/v1/users?search=tester')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('results', resp.data)
        usernames = [x['username'] for x in resp.data['results']]
        self.assertIn('tester', usernames)

    def test_admin_can_reset_password(self):
        login = self._login('platform_admin', 'Admin123!')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        resp = self.client.post(f'/api/v1/users/{self.normal_user.id}/reset-password', {'new_password': 'ResetPass123!'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        relogin = self._login('tester', 'ResetPass123!')
        self.assertEqual(relogin.status_code, status.HTTP_200_OK)

    def test_root_returns_frontend_landing_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('平台基础能力控制台', resp.content.decode('utf-8'))

class CustomerProjectModuleTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.pm = User.objects.create_user(username='pm1', email='pm1@test.com', password='Pm123456!')
        self.tester = User.objects.create_user(username='tester2', email='tester2@test.com', password='Tester123!')
        self.pm_role, _ = Role.objects.get_or_create(code='PM', defaults={'name': 'Project Manager'})
        self.tester_role, _ = Role.objects.get_or_create(code='TESTER', defaults={'name': 'Tester'})
        UserRole.objects.create(user=self.pm, role=self.pm_role, scope_type=UserRole.ScopeType.GLOBAL)
        UserRole.objects.create(user=self.tester, role=self.tester_role, scope_type=UserRole.ScopeType.GLOBAL)

    def _token(self, u, p):
        return self.client.post('/api/v1/auth/login', {'username': u, 'password': p}, format='json').data['access']

    def test_pm_can_create_customer_project(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token('pm1', 'Pm123456!')}")
        c = self.client.post('/api/v1/customers', {'name': 'ACME', 'code': 'acme', 'status': 'active'}, format='json')
        self.assertEqual(c.status_code, status.HTTP_201_CREATED)
        p = self.client.post('/api/v1/projects', {'customer': c.data['id'], 'name': 'Web', 'code': 'web', 'test_type': 'web'}, format='json')
        self.assertEqual(p.status_code, status.HTTP_201_CREATED)

    def test_tester_readonly_customer(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token('tester2', 'Tester123!')}")
        resp = self.client.post('/api/v1/customers', {'name': 'Bad', 'code': 'bad'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class ProjectAssetVisibilityTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(username='admin1', email='admin1@test.com', password='Admin123!')
        self.tester = User.objects.create_user(username='tester3', email='tester3@test.com', password='Tester123!')
        self.other = User.objects.create_user(username='tester4', email='tester4@test.com', password='Tester123!')

        admin_role, _ = Role.objects.get_or_create(code='ADMIN', defaults={'name': 'Admin'})
        tester_role, _ = Role.objects.get_or_create(code='TESTER', defaults={'name': 'Tester'})
        UserRole.objects.create(user=self.admin, role=admin_role, scope_type=UserRole.ScopeType.GLOBAL)
        UserRole.objects.create(user=self.tester, role=tester_role, scope_type=UserRole.ScopeType.GLOBAL)
        UserRole.objects.create(user=self.other, role=tester_role, scope_type=UserRole.ScopeType.GLOBAL)

        self.customer = Customer.objects.create(name='Acme', code='acme')
        self.p1 = Project.objects.create(customer=self.customer, name='P1', code='p1', created_by=self.admin)
        self.p2 = Project.objects.create(customer=self.customer, name='P2', code='p2', created_by=self.admin)

        ProjectMember.objects.create(project=self.p1, user=self.tester, member_type=ProjectMember.MemberType.TESTER)
        Asset.objects.create(project=self.p1, name='asset-1', asset_type=Asset.AssetType.HOST)
        Asset.objects.create(project=self.p2, name='asset-2', asset_type=Asset.AssetType.HOST)

    def _token(self, username, password):
        return self.client.post('/api/v1/auth/login', {'username': username, 'password': password}, format='json').data['access']

    def test_admin_can_see_all_projects(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token('admin1', 'Admin123!')}")
        resp = self.client.get('/api/v1/projects')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data['count'], 2)

    def test_tester_only_sees_assigned_projects_and_assets(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token('tester3', 'Tester123!')}")
        p_resp = self.client.get('/api/v1/projects')
        self.assertEqual(p_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(p_resp.data['count'], 1)
        self.assertEqual(p_resp.data['results'][0]['code'], 'p1')

        a_resp = self.client.get('/api/v1/assets')
        self.assertEqual(a_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(a_resp.data['count'], 1)
        self.assertEqual(a_resp.data['results'][0]['name'], 'asset-1')


class BatchFindingApiTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.pm = User.objects.create_user(username='pmx', email='pmx@test.com', password='Pm123456!')
        self.tester = User.objects.create_user(username='tx', email='tx@test.com', password='Tester123!')
        self.qa = User.objects.create_user(username='qax', email='qax@test.com', password='Qa123456!')
        pm_role, _ = Role.objects.get_or_create(code='PM', defaults={'name': 'PM'})
        tester_role, _ = Role.objects.get_or_create(code='TESTER', defaults={'name': 'Tester'})
        qa_role, _ = Role.objects.get_or_create(code='QA', defaults={'name': 'QA'})
        UserRole.objects.create(user=self.pm, role=pm_role, scope_type=UserRole.ScopeType.GLOBAL)
        UserRole.objects.create(user=self.tester, role=tester_role, scope_type=UserRole.ScopeType.GLOBAL)
        UserRole.objects.create(user=self.qa, role=qa_role, scope_type=UserRole.ScopeType.GLOBAL)

        self.customer = Customer.objects.create(name='C1', code='c1')
        self.project = Project.objects.create(customer=self.customer, name='Proj', code='proj', project_manager=self.pm, created_by=self.pm)
        ProjectMember.objects.create(project=self.project, user=self.tester, member_type=ProjectMember.MemberType.TESTER)
        ProjectMember.objects.create(project=self.project, user=self.qa, member_type=ProjectMember.MemberType.QA)
        self.asset = Asset.objects.create(project=self.project, name='a1', asset_type=Asset.AssetType.HOST)

    def _token(self, username, password):
        return self.client.post('/api/v1/auth/login', {'username': username, 'password': password}, format='json').data['access']

    def test_tester_can_create_batch_and_qa_readonly_finding(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token('tx', 'Tester123!')}")
        b = self.client.post('/api/v1/batches', {'asset_id': str(self.asset.id), 'name': 'B1', 'batch_no': '2026-001', 'status': 'testing'}, format='json')
        self.assertEqual(b.status_code, status.HTTP_201_CREATED)

        f = self.client.post('/api/v1/findings', {'asset_id': str(self.asset.id), 'batch_id': b.data['id'], 'title': 'XSS', 'severity': 'high', 'status': 'open'}, format='json')
        self.assertEqual(f.status_code, status.HTTP_201_CREATED)

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self._token('qax', 'Qa123456!')}")
        ro = self.client.patch(f"/api/v1/findings/{f.data['id']}", {'status': 'fixed'}, format='json')
        self.assertEqual(ro.status_code, status.HTTP_403_FORBIDDEN)

        hist = self.client.get(f"/api/v1/history-findings?asset_id={self.asset.id}")
        self.assertEqual(hist.status_code, status.HTTP_200_OK)
