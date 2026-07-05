from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            'measurements',
            '0006_category_externally_synced_category_metric_type_and_more',
        ),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_official',
            field=models.BooleanField(default=False, verbose_name='Official category'),
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(
                condition=models.Q(('is_official', True)),
                fields=('user', 'metric_type'),
                name='unique_official_category_per_metric_type',
            ),
        ),
    ]
