from rest_framework import serializers

from users.models import Role, User, UserRole


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    roles = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name', 'is_active', 'is_staff', 'password', 'roles', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def get_roles(self, obj):
        return sorted(set(obj.user_roles.values_list('role__code', flat=True)))


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'code', 'name', 'description', 'is_system', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'user', 'role', 'scope_type', 'customer', 'project', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, attrs):
        scope_type = attrs.get('scope_type', getattr(self.instance, 'scope_type', None))
        customer = attrs.get('customer', getattr(self.instance, 'customer', None))
        project = attrs.get('project', getattr(self.instance, 'project', None))

        if scope_type == UserRole.ScopeType.GLOBAL and (customer or project):
            raise serializers.ValidationError('GLOBAL scope must not bind customer/project')
        if scope_type == UserRole.ScopeType.CUSTOMER and not customer:
            raise serializers.ValidationError('customer is required for CUSTOMER scope')
        if scope_type == UserRole.ScopeType.CUSTOMER and project:
            raise serializers.ValidationError('CUSTOMER scope must not bind project')
        if scope_type == UserRole.ScopeType.PROJECT and not project:
            raise serializers.ValidationError('project is required for PROJECT scope')
        return attrs
