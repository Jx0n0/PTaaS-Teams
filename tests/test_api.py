from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from business.models import Asset, Customer, Project
from users.models import Role, UserRole


class APISmokeTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.admin = User.objects.create_user(
            username='admin', email='admin@test.com', password='Admin123!', is_staff=True, is_superuser=True
        )
        self.pm = User.objects.create_user(username='pm', email='pm@test.com', password='Pm123456!')
        self.tester = User.objects.create_user(username='tester', email='tester@test.com', password='Tester123!')
        self.qa = User.objects.create_user(username='qa', email='qa@test.com', password='Qa123456!')

        self.admin_role = Role.objects.create(code='admin', name='Admin')
        self.pm_role = Role.objects.create(code='pm', name='PM')
        self.tester_role = Role.objects.create(code='tester', name='Tester')
        self.qa_role = Role.objects.create(code='qa', name='QA')

        self.customer = Customer.objects.create(code='acme', name='ACME')
        self.project = Project.objects.create(customer=self.customer, code='web', name='Web')

        UserRole.objects.create(user=self.pm, role=self.pm_role, scope_type=UserRole.ScopeType.PROJECT, project=self.project)
        UserRole.objects.create(user=self.tester, role=self.tester_role, scope_type=UserRole.ScopeType.PROJECT, project=self.project)
        UserRole.objects.create(user=self.qa, role=self.qa_role, scope_type=UserRole.ScopeType.PROJECT, project=self.project)

    def _token(self, username, password):
        resp = self.client.post(reverse('token_obtain_pair'), {'username': username, 'password': password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        return resp.data['access']

    def test_admin_can_create_customer(self):
        token = self._token('admin', 'Admin123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resp = self.client.post('/api/customers/', {'code': 'globex', 'name': 'Globex'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_pm_can_create_project(self):
        token = self._token('pm', 'Pm123456!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resp = self.client.post('/api/projects/', {'customer': self.customer.id, 'code': 'api', 'name': 'API Test'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_tester_can_create_asset(self):
        token = self._token('tester', 'Tester123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resp = self.client.post(
            '/api/assets/',
            {'project': self.project.id, 'name': 'Main Domain', 'asset_type': 'DOMAIN', 'value': 'acme.com', 'criticality': 3},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_qa_cannot_create_asset(self):
        token = self._token('qa', 'Qa123456!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resp = self.client.post(
            '/api/assets/',
            {'project': self.project.id, 'name': 'Main Domain', 'asset_type': 'DOMAIN', 'value': 'acme.com', 'criticality': 3},
            format='json',
        )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_root_redirects_to_admin(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, status.HTTP_302_FOUND)
        self.assertEqual(resp.headers['Location'], '/admin/')

    def test_scoped_user_only_sees_assigned_project_assets(self):
        other_customer = Customer.objects.create(code='initech', name='Initech')
        other_project = Project.objects.create(customer=other_customer, code='ext', name='External')
        Asset.objects.create(project=self.project, name='In Scope', asset_type='DOMAIN', value='acme.com')
        Asset.objects.create(project=other_project, name='Out Scope', asset_type='DOMAIN', value='initech.com')

        token = self._token('tester', 'Tester123!')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resp = self.client.get('/api/assets/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        names = [item['name'] for item in resp.data]
        self.assertIn('In Scope', names)
        self.assertNotIn('Out Scope', names)
