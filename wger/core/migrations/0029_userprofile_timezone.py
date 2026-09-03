# Django
from django.db import migrations, models

# wger
from wger.core.models.profile import validate_timezone


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0028_longlivedsession'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='time_zone',
            field=models.CharField(
                blank=True,
                default='',
                help_text='IANA timezone name, e.g. "Europe/Berlin". Empty means no '
                'client has reported one and the instance timezone is used.',
                max_length=50,
                validators=[validate_timezone],
                verbose_name='Timezone',
            ),
        ),
    ]
