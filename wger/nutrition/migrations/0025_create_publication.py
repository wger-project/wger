from django.db import migrations

from wger.utils.db import is_postgres_db

# TODO move to more appropriate place

def add_publication(apps, schema_editor):
    if is_postgres_db():
        schema_editor.execute(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_publication WHERE pubname = 'powersync'
                ) THEN
                    CREATE PUBLICATION powersync FOR ALL TABLES;
                END IF;
            END $$;
            """
        )


def remove_publication(apps, schema_editor):
    if is_postgres_db():
        schema_editor.execute('DROP PUBLICATION IF EXISTS powersync;')


class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0024_remove_ingredient_status'),
    ]

    operations = [
        migrations.RunPython(add_publication, reverse_code=remove_publication),
    ]
