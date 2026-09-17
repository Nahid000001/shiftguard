from django.db import migrations


def backfill_owner(apps, schema_editor):
    Agency = apps.get_model("agencies", "Agency")
    User = apps.get_model("auth", "User")
    owner = User.objects.filter(is_superuser=True).order_by("id").first() or User.objects.order_by("id").first()
    if owner:
        Agency.objects.filter(user__isnull=True).update(user=owner)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("agencies", "0002_agency_user"),
    ]

    operations = [
        migrations.RunPython(backfill_owner, noop_reverse),
    ]
