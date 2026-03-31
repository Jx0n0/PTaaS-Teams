from business.models import Asset, Batch, Customer, Project
from users.models import UserRole


class ScopeService:
    ADMIN_ROLE_CODE = 'ADMIN'
    PM_ROLE_CODE = 'PM'
    TESTER_ROLE_CODE = 'TESTER'
    QA_ROLE_CODE = 'QA'

    @classmethod
    def is_admin(cls, user):
        return user.is_superuser or UserRole.objects.filter(user=user, role__code=cls.ADMIN_ROLE_CODE).exists()

    @classmethod
    def role_queryset(cls, user):
        return UserRole.objects.select_related('customer', 'project', 'role').filter(user=user)

    @classmethod
    def has_role(cls, user, role_codes):
        if cls.is_admin(user):
            return True
        return cls.role_queryset(user).filter(role__code__in=role_codes).exists()

    @classmethod
    def customer_ids(cls, user):
        roles = cls.role_queryset(user)
        direct = roles.filter(scope_type=UserRole.ScopeType.CUSTOMER).values_list('customer_id', flat=True)
        project_based = Project.objects.filter(
            id__in=roles.filter(scope_type=UserRole.ScopeType.PROJECT).values_list('project_id', flat=True)
        ).values_list('customer_id', flat=True)
        return set(direct).union(set(project_based))

    @classmethod
    def project_ids(cls, user):
        roles = cls.role_queryset(user)
        direct = roles.filter(scope_type=UserRole.ScopeType.PROJECT).values_list('project_id', flat=True)
        via_customer = Project.objects.filter(
            customer_id__in=roles.filter(scope_type=UserRole.ScopeType.CUSTOMER).values_list('customer_id', flat=True)
        ).values_list('id', flat=True)
        return set(direct).union(set(via_customer))

    @classmethod
    def can_manage_customer_project(cls, user):
        return cls.is_admin(user) or cls.has_role(user, [cls.PM_ROLE_CODE])

    @classmethod
    def can_manage_asset_batch(cls, user):
        return cls.is_admin(user) or cls.has_role(user, [cls.PM_ROLE_CODE, cls.TESTER_ROLE_CODE])

    @classmethod
    def filter_queryset(cls, user, queryset):
        if cls.is_admin(user):
            return queryset

        model = queryset.model
        customer_ids = cls.customer_ids(user)
        project_ids = cls.project_ids(user)
        if model is Customer:
            return queryset.filter(id__in=customer_ids)
        if model is Project:
            return queryset.filter(id__in=project_ids)
        if model is Asset:
            return queryset.filter(project_id__in=project_ids)
        if model is Batch:
            return queryset.filter(asset__project_id__in=project_ids)
        return queryset.none()

    @classmethod
    def can_access_obj(cls, user, obj):
        if cls.is_admin(user):
            return True
        if isinstance(obj, Customer):
            return obj.id in cls.customer_ids(user)
        if isinstance(obj, Project):
            return obj.id in cls.project_ids(user)
        if isinstance(obj, Asset):
            return obj.project_id in cls.project_ids(user)
        if isinstance(obj, Batch):
            return obj.asset.project_id in cls.project_ids(user)
        return False
