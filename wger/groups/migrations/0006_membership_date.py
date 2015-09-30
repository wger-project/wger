# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.datetime_safe


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0005_auto_20150930_1514'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='date',
            field=models.DateField(verbose_name='Date', default=django.utils.datetime_safe.date.today, auto_now_add=True),
            preserve_default=False,
        ),
    ]
