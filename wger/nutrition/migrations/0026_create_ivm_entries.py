from django.db import migrations

from wger.utils.db import postgres_only


@postgres_only
def add_ivm_views(apps, schema_editor):
    """
    Note: the select statements are written a bit weirdly because of this issue
    https://github.com/sraoss/pg_ivm/issues/85

    When this is resolved, we can remove the subqueries and write e.g.

    SELECT m.*, p.user_id
    FROM nutrition_meal AS m
    JOIN nutrition_nutritionplan AS p ON m.plan_id = p.id;
    """

    schema_editor.execute(
        """
        SELECT create_immv(
            'ivm_nutrition_nutritionplan',
            'SELECT
                p.uuid AS id,
                p.id AS remote_id,
                creation_date,
                description,
                has_goal_calories,
                user_id,
                only_logging,
                goal_carbohydrates,
                goal_energy,
                goal_fat,
                goal_protein,
                goal_fiber
            FROM nutrition_nutritionplan AS p;'
        );
        """
    )

    schema_editor.execute(
        """
        SELECT create_immv(
            'ivm_nutrition_meal',
            'SELECT
                m.uuid AS id,
                m.id AS remote_id,
                "order",
                time,
                p.uuid AS plan_id,
                name,
                p.user_id
             FROM (SELECT * FROM nutrition_meal) AS m
             JOIN (SELECT id, uuid, user_id FROM nutrition_nutritionplan) AS p ON m.plan_id = p.id;'
        );
        """
    )

    schema_editor.execute(
        """
        SELECT create_immv(
            'ivm_nutrition_mealitem',
            'SELECT
                mi.uuid AS id,
                mi.id AS remote_id,
                "order",
                amount,
                ingredient_id,
                m.uuid AS meal_id,
                weight_unit_id,
                p.user_id
             FROM (SELECT * FROM nutrition_mealitem) AS mi
             JOIN (SELECT id, uuid, plan_id FROM nutrition_meal) AS m ON mi.meal_id = m.id
             JOIN (SELECT id, user_id FROM nutrition_nutritionplan) AS p ON m.plan_id = p.id;'
        );
        """
    )

    schema_editor.execute(
        """
        SELECT create_immv(
            'ivm_nutrition_logitem',
            'SELECT
                li.uuid as id,
                li.id AS remote_id,
                datetime,
                comment,
                amount,
                ingredient_id,
                p.uuid AS plan_id,
                weight_unit_id,
                m.uuid AS meal_id,
                p.user_id
             FROM (SELECT * FROM nutrition_logitem) AS li
             JOIN (SELECT id, uuid FROM nutrition_meal) AS m ON li.meal_id = m.id
             JOIN (SELECT id, uuid, user_id FROM nutrition_nutritionplan) AS p ON li.plan_id = p.id;'
            );
        """
    )


@postgres_only
def remove_ivm_views(apps, schema_editor):
    schema_editor.execute('DROP TABLE IF EXISTS ivm_nutrition_nutritionplan;')
    schema_editor.execute('DROP TABLE IF EXISTS ivm_nutrition_meal;')
    schema_editor.execute('DROP TABLE IF EXISTS ivm_nutrition_mealitem;')
    schema_editor.execute('DROP TABLE IF EXISTS ivm_nutrition_logitem;')


class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0025_add_uuids'),
        ('core', '0018_create_publication_add_ivm_extension'),
    ]

    operations = [
        migrations.RunPython(add_ivm_views, reverse_code=remove_ivm_views),
    ]
