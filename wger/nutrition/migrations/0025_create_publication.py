from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0024_remove_ingredient_status'),
    ]

    operations = [
        migrations.RunSQL(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_publication WHERE pubname = 'powersync'
                ) THEN
                    CREATE PUBLICATION powersync FOR TABLE nutrition_ingredient, auth_user;
                END IF;
            END $$;
            """,
            reverse_sql="""
            DROP PUBLICATION IF EXISTS powersync;
            """
        ),
    ]
