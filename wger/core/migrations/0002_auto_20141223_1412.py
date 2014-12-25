# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='routines_round_to',
            field=models.DecimalField(decimal_places=2, default=1.25, max_digits=4, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)], help_text='The weight of the smallest plate you have available. On routines and schedules the calculated  weight will be rounded UP to the next multiple of this value.', verbose_name='Round weight in routines'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='weight_unit',
            field=models.CharField(default=b'kg', help_text='Select your preferred unit. This setting controls how the weight entries are interpreted if there are any calculations as well as their display.', max_length=2, verbose_name='Weight unit', choices=[(b'kg', 'Metric (kilogram)'), (b'lb', 'Imperial (pound)')]),
            preserve_default=True,
        ),
    ]
