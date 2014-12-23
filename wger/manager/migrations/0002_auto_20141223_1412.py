# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeightConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('increment_mode', models.CharField(default=b'static', help_text='Select the mode by which the weight increase is determined. "Static" increases the weight by a specific amount, "dynamic" can do that based on your workout performance.', max_length=7, verbose_name='Mode', choices=[(b'static', 'Static'), (b'dynamic', 'Dynamic')])),
                ('dynamic_mode', models.CharField(default=b'last', help_text='Select the time frame used to select your base weight.', max_length=7, verbose_name='Dynamic mode', choices=[(b'last', 'Last workout'), (b'2weeks', 'Best workout in last 2 weeks'), (b'4weeks', 'Best workout in last 4 weeks')])),
                ('start', models.DecimalField(verbose_name='Starting weight', max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(400)])),
                ('increment', models.DecimalField(verbose_name='Weekly weight increment', max_digits=4, decimal_places=2, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('weight_unit', models.CharField(default=b'kg', max_length=2, verbose_name='Weight unit', choices=[(b'kg', 'Metric (kilogram)'), (b'lb', 'Imperial (pound)')])),
                ('value', models.CharField(default=b'weight', max_length=2, verbose_name='Weight unit', choices=[(b'weight', 'Constant value'), (b'percent', 'Percent')])),
                ('schedule_step', models.ForeignKey(editable=False, to='manager.ScheduleStep')),
                ('setting', models.ForeignKey(editable=False, to='manager.Setting')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='weightconfig',
            unique_together=set([('schedule_step', 'setting')]),
        ),
    ]
