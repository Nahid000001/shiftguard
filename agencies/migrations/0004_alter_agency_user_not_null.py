import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("agencies", "0003_backfill_agency_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="agency",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="agencies",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
