# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_repetitionunit'),
    ]

    operations = [
        migrations.CreateModel(
            name='WeightUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=100)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
