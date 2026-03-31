from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('business', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userrole',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='user_roles', to='business.customer'),
        ),
        migrations.AddField(
            model_name='userrole',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='user_roles', to='business.project'),
        ),
        migrations.AddConstraint(
            model_name='userrole',
            constraint=models.UniqueConstraint(fields=('user', 'role', 'scope_type', 'customer', 'project'), name='uniq_user_role_scope'),
        ),
    ]
