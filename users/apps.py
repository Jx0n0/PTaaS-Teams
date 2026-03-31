from django.apps import AppConfig
from django.db.models.signals import post_migrate


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        post_migrate.connect(create_builtin_roles, sender=self)


def create_builtin_roles(**kwargs):
    from users.models import Role

    defaults = [
        ('ADMIN', 'Admin'),
        ('PM', 'Project Manager'),
        ('TESTER', 'Tester'),
        ('QA', 'QA'),
    ]
    for code, name in defaults:
        Role.objects.get_or_create(code=code, defaults={'name': name, 'is_system': True})
