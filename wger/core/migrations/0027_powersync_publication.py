from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps

from wger.utils.db import postgres_only


"""
Creates the publication PowerSync replicates from.

Migration 0023 created it "FOR ALL TABLES", but only a database superuser may do
that. Managed database services (Cloudron, most DBaaS products) hand out regular
roles, so the migration aborted the whole first migrate there. Listing the tables
one by one only requires owning them.

The list must contain every table the sync rules reference, including the ones
that only appear in a parameter query. When a table is added to the sync rules,
it needs a new migration adding it here:

    ALTER PUBLICATION powersync ADD TABLE <table>;
"""

TABLES = [
    'core_language',
    'core_license',
    'core_repetitionunit',
    'core_userprofile',
    'core_weightunit',
    'exercises_alias',
    'exercises_equipment',
    'exercises_exercise',
    'exercises_exercise_equipment',
    'exercises_exercise_muscles',
    'exercises_exercise_muscles_secondary',
    'exercises_exercisecategory',
    'exercises_exercisecomment',
    'exercises_exerciseimage',
    'exercises_exercisevideo',
    'exercises_muscle',
    'exercises_translation',
    'gallery_image',
    'manager_routine',
    'manager_workoutlog',
    'manager_workoutsession',
    'measurements_category',
    'measurements_measurement',
    'nutrition_image',
    'nutrition_ingredientweightunit',
    'nutrition_logitem',
    'nutrition_meal',
    'nutrition_mealitem',
    'nutrition_nutritionplan',
    'nutrition_synced_ingredient',
    'weight_weightentry',
]


@postgres_only
def add_publication(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor):
    # Installations from before 2.7 already have a publication for all tables. Postgres
    # doesn't allow changing the table list of those, and recreating the publication
    # would interrupt a running replication, so leave them alone.
    schema_editor.execute(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_publication WHERE pubname = 'powersync'
            ) THEN
                CREATE PUBLICATION powersync FOR TABLE {', '.join(TABLES)};
            END IF;
        END $$;
        """
    )


@postgres_only
def remove_publication(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor):
    schema_editor.execute('DROP PUBLICATION IF EXISTS powersync;')


class Migration(migrations.Migration):
    # All tables in the list must exist by the time this runs
    dependencies = [
        ('core', '0026_alter_userprofile_birthdate_alter_userprofile_height'),
        ('exercises', '0040_alter_exercise_license_author_and_more'),
        ('gallery', '0001_initial'),
        ('manager', '0028_backfill_session_day'),
        ('measurements', '0005_alter_measurement_date'),
        ('nutrition', '0037_powersync_synced_ingredient_tables'),
        ('weight', '0005_add_uuid'),
    ]

    operations = [
        migrations.RunPython(add_publication, reverse_code=remove_publication),
    ]
