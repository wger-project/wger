# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_settingunit'),
        ('manager', '0004_auto_20150609_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='unit',
            field=models.ForeignKey(default=1, to='core.SettingUnit', verbose_name='Unit'),
            preserve_default=False,
        ),
    ]
