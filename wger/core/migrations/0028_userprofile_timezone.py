# Django
from django.db import migrations, models

# wger
from wger.core.models.profile import validate_timezone


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0027_powersync_publication'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='time_zone',
            field=models.CharField(
                blank=True,
                default='',
                max_length=50,
                validators=[validate_timezone],
                verbose_name='Timezone',
            ),
        ),
    ]
