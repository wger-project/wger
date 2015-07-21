# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_auto_20150719_2000'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([('group', 'user')]),
        ),
    ]
