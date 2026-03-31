from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('users', '0002_userrole_scope_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='token_version',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
