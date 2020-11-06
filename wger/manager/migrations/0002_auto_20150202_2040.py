# -*- coding: utf-8 -*-
# flake8: noqa
from django.db import models, migrations
from sortedm2m.operations import AlterSortedManyToManyField
import sortedm2m.fields


class Migration(migrations.Migration):

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = [
        AlterSortedManyToManyField(
            model_name='set',
            name='exercises',
            field=sortedm2m.fields.SortedManyToManyField(help_text=None, to='exercises.Exercise', verbose_name='Exercises'),
            preserve_default=True,
        )
    ]
