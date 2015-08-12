# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0003_auto_20150721_1915'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='membership',
            options={'ordering': ['-admin', 'user__username']},
        ),
    ]
