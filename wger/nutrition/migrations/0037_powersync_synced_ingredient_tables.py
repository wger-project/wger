from django.db import migrations
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps

from wger.utils.db import postgres_only

"""
Adds a slim shadow copy of nutrition_ingredient.

PowerSync materialises one bucket per *source row* a data query matches, so
syncing ``nutrition_ingredient`` directly creates one bucket per ingredient
(~3M) even though only the ingredients actually referenced by some log/meal
item are ever used. That bloats bucket storage and the initial-replication
footprint (the WAL grows ~25GB while the snapshot runs).

To avoid this the sync rules read ingredients from ``nutrition_synced_ingredient``,
a shadow table that holds only the *used* rows, kept in sync by DB triggers (this
makes sure that the data is mirrored regardless of how the write happens: ORM,
bulk_create, COPY, raw SQL).

Other tables such as ``nutrition_image`` and ``nutrition_ingredientweightunit``
are synced directly, since at least currently it doesn't seem necessary to add
any shadow tables of their own.


Keeping the shadow table in lockstep when the ingredient schema changes
-----------------------------------------------------------------------
``nutrition_synced_ingredient`` is a physical copy and the triggers/functions
copy with ``SELECT *``, so any structure change to ``nutrition_ingredient`` must
be mirrored here, in the SAME migration that alters the source model:

1. Mirror the change on ``nutrition_synced_ingredient``, e.g.
   ``ALTER TABLE nutrition_synced_ingredient ADD COLUMN <col> <type>;``
   (likewise for renames, drops and type changes, the columns must be kept
   identical in name, type and order).

2. Backfill the new column into existing shadow rows:
   ``UPDATE nutrition_synced_ingredient s SET <col> = i.<col>``
   ``FROM nutrition_ingredient i WHERE s.id = i.id;``
   This is required: Django's AddField-with-default is a metadata-only change on
   Postgres >= 11 and does NOT fire the AFTER UPDATE trigger, so existing shadow
   rows would otherwise keep NULL / the default.

3. The functions and triggers themselves need no change, as long as the shadow
   stays structurally identical. If it drifts, the ``SELECT *`` copy fails and
   log/meal-item INSERTs error out loudly -- that is the intended guard.
"""



SQL = [
    # Shadow table: structure cloned incl. PK (= replica identity for logical
    # replication). EXCLUDING IDENTITY so we can insert the explicit ids copied
    # from the source rows.
    """
    CREATE TABLE IF NOT EXISTS nutrition_synced_ingredient(
        LIKE nutrition_ingredient INCLUDING ALL EXCLUDING IDENTITY
    );
    """,

    # Copy an ingredient into the shadow set
    """
    CREATE OR REPLACE FUNCTION powersync_ensure_ingredient_synced(ing_id bigint)
        RETURNS void LANGUAGE sql AS $$
        INSERT INTO nutrition_synced_ingredient
            SELECT * FROM nutrition_ingredient WHERE id = ing_id
            ON CONFLICT (id) DO NOTHING;
    $$;
    """,

    # On every log and meal item, pull its ingredient into the shadow set.
    """
    CREATE OR REPLACE FUNCTION powersync_sync_ingredient_from_item()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            PERFORM powersync_ensure_ingredient_synced(NEW.ingredient_id);
            RETURN NEW;
        END $$;
    """,
    """
    CREATE TRIGGER powersync_sync_ingredient
        AFTER INSERT OR UPDATE OF ingredient_id ON nutrition_logitem
        FOR EACH ROW EXECUTE FUNCTION powersync_sync_ingredient_from_item();
    """,
    """
    CREATE TRIGGER powersync_sync_ingredient
        AFTER INSERT OR UPDATE OF ingredient_id ON nutrition_mealitem
        FOR EACH ROW EXECUTE FUNCTION powersync_sync_ingredient_from_item();
    """,

    # Keep already-synced ingredient rows fresh when the source changes.
    """
    CREATE OR REPLACE FUNCTION powersync_propagate_ingredient()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF EXISTS (SELECT 1 FROM nutrition_synced_ingredient WHERE id = NEW.id) THEN
                DELETE FROM nutrition_synced_ingredient WHERE id = NEW.id;
                INSERT INTO nutrition_synced_ingredient
                    SELECT * FROM nutrition_ingredient WHERE id = NEW.id;
            END IF;
            RETURN NEW;
        END $$;
    """,
    """
    CREATE TRIGGER powersync_propagate
        AFTER UPDATE ON nutrition_ingredient
        FOR EACH ROW EXECUTE FUNCTION powersync_propagate_ingredient();
    """,

    # Backfill everything already referenced by a log or meal item.
    """
    SELECT powersync_ensure_ingredient_synced(id) FROM (
        SELECT DISTINCT ingredient_id AS id FROM nutrition_logitem
        UNION
        SELECT DISTINCT ingredient_id       FROM nutrition_mealitem
    ) used;
    """,
]

REVERSE_SQL = [
    "DROP TRIGGER IF EXISTS powersync_propagate ON nutrition_ingredient;",
    "DROP TRIGGER IF EXISTS powersync_sync_ingredient ON nutrition_mealitem;",
    "DROP TRIGGER IF EXISTS powersync_sync_ingredient ON nutrition_logitem;",
    "DROP FUNCTION IF EXISTS powersync_propagate_ingredient();",
    "DROP FUNCTION IF EXISTS powersync_sync_ingredient_from_item();",
    "DROP FUNCTION IF EXISTS powersync_ensure_ingredient_synced(bigint);",
    "DROP TABLE IF EXISTS nutrition_synced_ingredient;",
]


@postgres_only
def create_synced_tables(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor):
    for statement in SQL:
        schema_editor.execute(statement)


@postgres_only
def drop_synced_tables(apps: StateApps, schema_editor: BaseDatabaseSchemaEditor):
    for statement in REVERSE_SQL:
        schema_editor.execute(statement)


class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0036_alter_image_license_author_and_more'),
    ]

    operations = [
        migrations.RunPython(create_synced_tables, reverse_code=drop_synced_tables),
    ]
