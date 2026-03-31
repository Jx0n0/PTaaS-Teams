from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from common.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class Role(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_system = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name} ({self.code})'


class UserRole(TimeStampedModel):
    class ScopeType(models.TextChoices):
        GLOBAL = 'GLOBAL', 'Global'
        CUSTOMER = 'CUSTOMER', 'Customer'
        PROJECT = 'PROJECT', 'Project'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    scope_type = models.CharField(max_length=20, choices=ScopeType.choices, default=ScopeType.GLOBAL)
    customer = models.ForeignKey('business.Customer', null=True, blank=True, on_delete=models.CASCADE, related_name='user_roles')
    project = models.ForeignKey('business.Project', null=True, blank=True, on_delete=models.CASCADE, related_name='user_roles')

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role', 'scope_type', 'customer', 'project'],
                name='uniq_user_role_scope',
            )
        ]

    def clean(self):
        if self.scope_type == self.ScopeType.GLOBAL and (self.customer_id or self.project_id):
            raise ValidationError('GLOBAL scope must not bind customer/project')
        if self.scope_type == self.ScopeType.CUSTOMER and not self.customer_id:
            raise ValidationError('customer is required for CUSTOMER scope')
        if self.scope_type == self.ScopeType.CUSTOMER and self.project_id:
            raise ValidationError('CUSTOMER scope must not bind project')
        if self.scope_type == self.ScopeType.PROJECT and not self.project_id:
            raise ValidationError('project is required for PROJECT scope')

    def __str__(self):
        return f'{self.user} -> {self.role} ({self.scope_type})'
