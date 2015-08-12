# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0004_auto_20150812_1554'),
        ('manager', '0004_auto_20150609_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='workout',
            name='group',
            field=models.ForeignKey(editable=False, to='groups.Group', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='schedulestep',
            name='order',
            field=models.IntegerField(default=1, verbose_name='Order'),
            preserve_default=True,
        ),
    ]
