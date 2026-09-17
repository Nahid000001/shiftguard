from django.db import migrations


def backfill_owner(apps, schema_editor):
    Licence = apps.get_model("licences", "Licence")
    User = apps.get_model("auth", "User")
    owner = User.objects.filter(is_superuser=True).order_by("id").first() or User.objects.order_by("id").first()
    if owner:
        Licence.objects.filter(user__isnull=True).update(user=owner)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("licences", "0002_licence_user"),
    ]

    operations = [
        migrations.RunPython(backfill_owner, noop_reverse),
    ]
