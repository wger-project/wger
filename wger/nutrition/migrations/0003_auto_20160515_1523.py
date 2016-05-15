# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nutrition', '0002_auto_20160510_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='status',
            field=models.CharField(editable=False, default='1', max_length=2, choices=[('1', 'Pending'), ('2', 'Accepted'), ('3', 'Declined'), ('4', 'Submitted by administrator'), ('5', 'System ingredient')]),
        ),
        migrations.AlterField(
            model_name='logitem',
            name='comment',
            field=models.TextField(blank=True, null=True, verbose_name='Comment'),
        ),
    ]
