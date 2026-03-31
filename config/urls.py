from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from config.views import root_landing
from users.auth_views import ChangePasswordView, LoginView, MeView, RefreshView
from users.views import RoleViewSet, UserRoleViewSet, UserViewSet
from business.views import AssetViewSet, BatchViewSet, CustomerViewSet, ProjectViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'batches', BatchViewSet, basename='batch')

urlpatterns = [
    path('', root_landing),
    path('admin/', admin.site.urls),
    path('api/v1/auth/login', LoginView.as_view(), name='auth_login'),
    path('api/v1/auth/refresh', RefreshView.as_view(), name='auth_refresh'),
    path('api/v1/auth/me', MeView.as_view(), name='auth_me'),
    path('api/v1/auth/change-password', ChangePasswordView.as_view(), name='auth_change_password'),
    path('api/v1/', include(router.urls)),
]
