# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_settingunit'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='settingunit',
            options={'ordering': ['name']},
        ),
    ]
