import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("licences", "0003_backfill_licence_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="licence",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="licences",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
