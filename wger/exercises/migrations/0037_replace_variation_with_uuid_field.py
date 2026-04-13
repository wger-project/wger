"""
Replace the Variation ForeignKey on Exercise with a UUID field.

Exercises with the same variation_group UUID belong to the same group.
The separate Variation model is no longer needed.

Steps:
1. Add UUID field to Variation model (so we have something to copy)
2. Add variation_group UUIDField to Exercise
3. Copy Variation UUIDs to Exercise.variation_group
4. Remove FK + delete model
"""

import uuid as uuid_mod

from django.db import migrations, models
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps


def fix_sqlite_historical_indexes(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor):
    """
    Fix index name collision caused by migration 0032_rename_exercise.

    When RenameModel renamed HistoricalExercise -> HistoricalTranslation and
    HistoricalExerciseBase -> HistoricalExercise, SQLite did not rename the
    indexes. The old exercises_historicalexercise_* indexes remain on the
    historicaltranslation table, colliding with indexes Django tries to
    create for the new HistoricalExercise model.

    This only affects SQLite; PostgreSQL renames indexes correctly.
    """
    if schema_editor.connection.vendor == 'postgresql':
        return

    cursor = schema_editor.connection.cursor()

    if schema_editor.connection.vendor == 'sqlite':
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' "
            "AND tbl_name='exercises_historicaltranslation' "
            "AND name LIKE 'exercises_historicalexercise_%'"
        )
        for (index_name,) in cursor.fetchall():
            cursor.execute(f'DROP INDEX IF EXISTS "{index_name}"')

    elif schema_editor.connection.vendor == 'mysql':
        cursor.execute(
            'SELECT INDEX_NAME FROM INFORMATION_SCHEMA.STATISTICS '
            "WHERE TABLE_NAME = 'exercises_historicaltranslation' "
            "AND INDEX_NAME LIKE 'exercises_historicalexercise_%%'"
        )
        for (index_name,) in cursor.fetchall():
            cursor.execute(f'DROP INDEX `{index_name}` ON `exercises_historicaltranslation`')


def generate_variation_uuids(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor):
    """Generate UUIDs for existing Variation objects."""
    Variation = apps.get_model('exercises', 'Variation')
    for variation in Variation.objects.all():
        variation.uuid = uuid_mod.uuid4()
        variation.save(update_fields=['uuid'])


def copy_variation_uuids(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor):
    """Copy the UUID from each Variation object to the exercises that reference it."""
    Exercise = apps.get_model('exercises', 'Exercise')
    for exercise in Exercise.objects.filter(variations__isnull=False).select_related('variations'):
        exercise.variation_group = exercise.variations.uuid
        exercise.save(update_fields=['variation_group'])


class Migration(migrations.Migration):
    dependencies = [
        ('exercises', '0036_add_markdown_description_field'),
    ]

    operations = [
        migrations.RunPython(fix_sqlite_historical_indexes, migrations.RunPython.noop),
        # Temporarily add UUID to the variation table
        migrations.AddField(
            model_name='variation',
            name='uuid',
            field=models.UUIDField(null=True),
        ),
        migrations.RunPython(generate_variation_uuids, migrations.RunPython.noop),
        migrations.AddField(
            model_name='exercise',
            name='variation_group',
            field=models.UUIDField(
                blank=True,
                db_index=True,
                null=True,
                verbose_name='Variation group',
            ),
        ),
        migrations.AddField(
            model_name='historicalexercise',
            name='variation_group',
            field=models.UUIDField(
                blank=True,
                null=True,
                verbose_name='Variation group',
            ),
        ),
        # Copy data and remove FK relations
        migrations.RunPython(copy_variation_uuids, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='exercise',
            name='variations',
        ),
        migrations.RemoveField(
            model_name='historicalexercise',
            name='variations',
        ),
        # Cleanup
        migrations.DeleteModel(
            name='Variation',
        ),
    ]
