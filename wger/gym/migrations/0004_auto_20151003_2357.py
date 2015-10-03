# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0003_auto_20151003_2008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='amount',
            field=models.DecimalField(default=0, verbose_name='Amount', max_digits=12, decimal_places=2),
        ),
    ]
