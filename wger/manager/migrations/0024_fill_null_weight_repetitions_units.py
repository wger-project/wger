from django.db import migrations
from django.db.migrations.state import StateApps


def fill_null_units_slot_entry(apps: StateApps, schema_editor):
    """
    Backfill all null unit values in SlotEntry with their defaults.
    REP_UNIT_REPETITIONS = 1 , WEIGHT_UNIT_KG = 1
    """
    SlotEntry = apps.get_model("manager", "SlotEntry")

    SlotEntry.objects.filter(repetition_unit__isnull=True).update(repetition_unit_id=1)
    SlotEntry.objects.filter(weight_unit__isnull=True).update(weight_unit_id=1)


def fill_null_units_workout_log(apps: StateApps, schema_editor):
    """
    Backfill all null unit values in WorkoutLog with their defaults.
    """
    WorkoutLog = apps.get_model("manager", "WorkoutLog")

    # Only fill repetitions_unit where repetitions is also not null
    WorkoutLog.objects.filter(
        repetitions_unit__isnull=True,
        repetitions__isnull=False,
    ).update(repetitions_unit_id=1)

    # Only fill weight_unit where weight is also not null
    WorkoutLog.objects.filter(
        weight_unit__isnull=True,
        weight__isnull=False,
    ).update(weight_unit_id=1)


class Migration(migrations.Migration):
    dependencies = [
        ("manager", "0023_change_validators"),
    ]

    operations = [
        migrations.RunPython(fill_null_units_slot_entry, fill_null_units_workout_log),
    ]
