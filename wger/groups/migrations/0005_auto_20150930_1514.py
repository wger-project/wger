# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0004_auto_20150812_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(verbose_name='Description', blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(verbose_name='Name', max_length=30, unique=True),
        ),
    ]
