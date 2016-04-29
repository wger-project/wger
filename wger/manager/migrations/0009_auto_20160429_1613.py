# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0008_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setting',
            name='reps',
            field=models.IntegerField(verbose_name='Amount', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(600)]),
        ),
    ]
