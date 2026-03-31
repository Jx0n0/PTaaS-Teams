from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import Role, UserRole


class AuthApiTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@test.com',
            password='OldPass123!',
            full_name='Demo Tester',
            is_active=True,
        )
        self.role = Role.objects.create(code='tester', name='Tester')
        UserRole.objects.create(user=self.user, role=self.role, scope_type=UserRole.ScopeType.GLOBAL)

    def test_login_returns_tokens_user_and_roles(self):
        resp = self.client.post('/api/v1/auth/login', {'username': 'tester', 'password': 'OldPass123!'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertEqual(resp.data['user']['username'], 'tester')
        self.assertIn('tester', resp.data['roles'])

    def test_me_returns_expected_fields(self):
        login = self.client.post('/api/v1/auth/login', {'username': 'tester', 'password': 'OldPass123!'}, format='json')
        token = login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        resp = self.client.get('/api/v1/auth/me')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(resp.data.keys()),
            {'id', 'username', 'email', 'full_name', 'is_active', 'roles'},
        )
        self.assertIn('tester', resp.data['roles'])

    def test_change_password_requires_old_password_and_confirmation(self):
        login = self.client.post('/api/v1/auth/login', {'username': 'tester', 'password': 'OldPass123!'}, format='json')
        token = login.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

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
        self.assertEqual(ok.data['message'], 'Password changed successfully.')

        re_login = self.client.post('/api/v1/auth/login', {'username': 'tester', 'password': 'NewPass123!'}, format='json')
        self.assertEqual(re_login.status_code, status.HTTP_200_OK)

    def test_refresh_token(self):
        login = self.client.post('/api/v1/auth/login', {'username': 'tester', 'password': 'OldPass123!'}, format='json')
        resp = self.client.post('/api/v1/auth/refresh', {'refresh': login.data['refresh']}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('access', resp.data)
