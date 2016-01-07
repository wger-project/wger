# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20151025_2237'),
    ]

    operations = [
        migrations.CreateModel(
            name='SettingUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
            ],
        ),
        migrations.RunSQL("INSERT INTO core_settingunit (name) VALUES ('Repetitions');")
    ]
