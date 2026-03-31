from django.db.models import Q
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from users.models import Role, User, UserRole
from users.permissions import IsPlatformAdmin
from users.serializers import ResetPasswordSerializer, RoleSerializer, UserRoleSerializer, UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('-created_at')
    serializer_class = UserSerializer
    permission_classes = [IsPlatformAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        username = self.request.query_params.get('username')
        email = self.request.query_params.get('email')
        full_name = self.request.query_params.get('full_name')
        is_active = self.request.query_params.get('is_active')
        search = self.request.query_params.get('search')

        if username:
            qs = qs.filter(username__icontains=username)
        if email:
            qs = qs.filter(email__icontains=email)
        if full_name:
            qs = qs.filter(full_name__icontains=full_name)
        if is_active in {'true', 'false'}:
            qs = qs.filter(is_active=(is_active == 'true'))
        if search:
            qs = qs.filter(Q(username__icontains=search) | Q(email__icontains=search) | Q(full_name__icontains=search))
        return qs

    @action(detail=True, methods=['post'], url_path='reset-password')
    def reset_password(self, request, pk=None):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.token_version += 1
        user.save(update_fields=['password', 'token_version'])
        return Response({'message': 'Password reset successfully.'})


class RoleViewSet(ModelViewSet):
    queryset = Role.objects.all().order_by('code')
    serializer_class = RoleSerializer
    permission_classes = [IsPlatformAdmin]


class UserRoleViewSet(ModelViewSet):
    queryset = UserRole.objects.select_related('user', 'role', 'customer', 'project').all().order_by('-created_at')
    serializer_class = UserRoleSerializer
    permission_classes = [IsPlatformAdmin]
