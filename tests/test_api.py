from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import Role, UserRole


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

        self.admin_role = Role.objects.create(code='admin', name='Admin')
        self.tester_role = Role.objects.create(code='tester', name='Tester')
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
        self.assertIn('tester', resp.data['roles'])

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
            {'old_password': 'wrong', 'new_password': 'NewPass123!', 'new_password_confirm': 'NewPass123!'},
            format='json',
        )
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)

        ok = self.client.post(
            '/api/v1/auth/change-password',
            {'old_password': 'OldPass123!', 'new_password': 'NewPass123!', 'new_password_confirm': 'NewPass123!'},
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
            '/api/v1/users/',
            {'username': 'pm1', 'email': 'pm1@test.com', 'full_name': 'PM 1', 'password': 'Pm123456!'},
            format='json',
        )
        self.assertEqual(create_user.status_code, status.HTTP_201_CREATED)

        create_role = self.client.post('/api/v1/roles/', {'code': 'pm', 'name': 'Project Manager'}, format='json')
        self.assertEqual(create_role.status_code, status.HTTP_201_CREATED)

        bind = self.client.post(
            '/api/v1/user-roles/',
            {'user': create_user.data['id'], 'role': create_role.data['id'], 'scope_type': 'GLOBAL'},
            format='json',
        )
        self.assertEqual(bind.status_code, status.HTTP_201_CREATED)

    def test_non_admin_cannot_manage_user_role(self):
        login = self._login('tester', 'OldPass123!')
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login.data['access']}")

        resp = self.client.get('/api/v1/users/')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_root_returns_frontend_landing_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('PTaaS Teams 平台入口', resp.content.decode('utf-8'))
