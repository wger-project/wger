import uuid as uuid_mod
from django.db import migrations, models
from django.db.migrations.state import StateApps


def generate_variation_uuids(apps: StateApps, schema_editor):
    Variation = apps.get_model('exercises', 'Variation')
    for variation in Variation.objects.all():
        variation.uuid = uuid_mod.uuid4()
        variation.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0035_add_is_ai_generated'),
    ]

    operations = [
        migrations.AddField(
            model_name='variation',
            name='uuid',
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(generate_variation_uuids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='variation',
            name='uuid',
            field=models.UUIDField(default=uuid_mod.uuid4, editable=False, unique=True),
        ),
    ]
