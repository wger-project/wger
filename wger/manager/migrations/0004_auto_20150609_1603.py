# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0002_auto_20150202_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='weight',
            field=models.DecimalField(decimal_places=2, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1500)], max_digits=6, blank=True, null=True, verbose_name='Weight'),
            preserve_default=True,
        ),
    ]
