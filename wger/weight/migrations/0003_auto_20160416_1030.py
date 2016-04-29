# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('weight', '0002_auto_20150604_2139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weightentry',
            name='weight',
            field=models.DecimalField(decimal_places=2, verbose_name='Weight', validators=[django.core.validators.MinValueValidator(30), django.core.validators.MaxValueValidator(600)], max_digits=5),
        ),
    ]
