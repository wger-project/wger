# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20150217_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='num_days_weight_reminder',
            field=models.IntegerField(default=0, verbose_name='Automatic reminders for weight entries', max_length=30, help_text='Number of days after the last weight entry (enter 0 to deactivate)'),
            preserve_default=True,
        ),
    ]
