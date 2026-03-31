from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('business', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customer',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('archived', 'Archived')], default='active', max_length=20),
        ),
        migrations.AddField(
            model_name='project',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='project',
            name='description',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='project',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='start_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('active', 'Active'), ('closed', 'Closed')], default='draft', max_length=20),
        ),
        migrations.AddField(
            model_name='project',
            name='test_type',
            field=models.CharField(choices=[('web', 'Web'), ('app', 'App'), ('api', 'API'), ('internal', 'Internal')], default='web', max_length=20),
        ),
        migrations.CreateModel(
            name='ReportTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('version', models.CharField(default='v1', max_length=50)),
                ('file_name', models.CharField(max_length=255)),
                ('storage_key', models.CharField(max_length=500)),
                ('file', models.FileField(upload_to='report_templates/')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='report_templates', to='business.customer')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('generating', 'Generating'), ('ready', 'Ready'), ('sent', 'Sent')], default='draft', max_length=20)),
                ('generated_file_key', models.CharField(blank=True, max_length=500)),
                ('generated_file', models.FileField(blank=True, null=True, upload_to='reports/')),
                ('asset', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='reports', to='business.asset')),
                ('batch', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.CASCADE, related_name='reports', to='business.batch')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('customer', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='reports', to='business.customer')),
                ('project', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='reports', to='business.project')),
                ('template', models.ForeignKey(on_delete=models.deletion.CASCADE, related_name='reports', to='business.reporttemplate')),
            ],
        ),
    ]
