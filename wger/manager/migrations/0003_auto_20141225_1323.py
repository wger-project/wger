# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_auto_20141223_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weightconfig',
            name='dynamic_mode',
            field=models.CharField(max_length=7, choices=[('last', 'Last workout'), ('2weeks', 'Best workout in last 2 weeks'), ('4weeks', 'Best workout in last 4 weeks')], help_text='Select the time frame used to select your base weight.', default='last', verbose_name='Dynamic mode'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weightconfig',
            name='increment_mode',
            field=models.CharField(max_length=7, choices=[('static', 'Static'), ('dynamic', 'Dynamic')], help_text='Select the mode by which the weight increase is determined. "Static" increases the weight by a specific amount, "dynamic" can do that based on your workout performance.', default='static', verbose_name='Mode'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weightconfig',
            name='value',
            field=models.CharField(max_length=7, choices=[('weight', 'Constant value'), ('percent', 'Percent')], default='weight', verbose_name='Weight unit'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='weightconfig',
            name='weight_unit',
            field=models.CharField(max_length=2, choices=[('kg', 'Metric (kilogram)'), ('lb', 'Imperial (pound)')], default='kg', verbose_name='Weight unit'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='workoutsession',
            name='impression',
            field=models.CharField(max_length=2, choices=[('1', 'Bad'), ('2', 'Neutral'), ('3', 'Good')], help_text='Your impression about this workout session. Did you exercise as well as you could?', default='2', verbose_name='General impression'),
            preserve_default=True,
        ),
    ]
