from rest_framework.viewsets import ModelViewSet

from users.models import Role, User, UserRole
from users.permissions import IsPlatformAdmin
from users.serializers import RoleSerializer, UserRoleSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [IsPlatformAdmin]


class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all().order_by('id')
    serializer_class = RoleSerializer
    permission_classes = [IsPlatformAdmin]


class UserRoleViewSet(ModelViewSet):
    queryset = UserRole.objects.select_related('user', 'role', 'customer', 'project').all().order_by('id')
    serializer_class = UserRoleSerializer
    permission_classes = [IsPlatformAdmin]
