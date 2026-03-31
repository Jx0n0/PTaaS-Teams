from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.SlugField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={'ordering': ['id']},
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('code', models.SlugField(max_length=50)),
                ('name', models.CharField(max_length=200)),
                ('is_active', models.BooleanField(default=True)),
                ('customer', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='projects', to='business.customer')),
            ],
            options={'ordering': ['id']},
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('asset_type', models.CharField(choices=[('DOMAIN', 'Domain'), ('IP', 'IP'), ('URL', 'URL'), ('MOBILE', 'Mobile')], max_length=20)),
                ('value', models.CharField(max_length=500)),
                ('criticality', models.PositiveSmallIntegerField(default=3)),
                ('is_active', models.BooleanField(default=True)),
                ('project', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='assets', to='business.project')),
            ],
            options={'ordering': ['id']},
        ),
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('RUNNING', 'Running'), ('DONE', 'Done'), ('FAILED', 'Failed')], default='DRAFT', max_length=20)),
                ('scheduled_at', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('extra', models.JSONField(blank=True, default=dict)),
                ('asset', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='batches', to='business.asset')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={'ordering': ['id']},
        ),
        migrations.AddConstraint(
            model_name='project',
            constraint=models.UniqueConstraint(fields=('customer', 'code'), name='uniq_project_code_per_customer'),
        ),
    ]
