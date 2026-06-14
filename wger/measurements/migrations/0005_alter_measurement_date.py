import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    """This only changes de default"""

    dependencies = [
        ('measurements', '0004_add_uuids'),
    ]

    operations = [
        migrations.AlterField(
            model_name='measurement',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date'),
        ),
    ]
