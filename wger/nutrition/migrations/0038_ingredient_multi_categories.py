from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("nutrition", "0037_powersync_synced_ingredient_tables"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="ingredient",
            name="category",
        ),
        migrations.AddField(
            model_name="ingredient",
            name="category",
            field=models.ManyToManyField(
                blank=True,
                related_name="ingredients",
                to="nutrition.ingredientcategory",
                verbose_name="Category",
            ),
        ),
    ]
