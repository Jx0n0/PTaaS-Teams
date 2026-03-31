from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import RoleViewSet, UserRoleViewSet, UserViewSet
from business.views import AssetViewSet, BatchViewSet, CustomerViewSet, ProjectViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'batches', BatchViewSet, basename='batch')

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
]
