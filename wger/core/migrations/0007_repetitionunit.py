# -*- coding: utf-8 -*-
# flake8: noqa
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20151025_2237'),
    ]

    operations = [
        migrations.CreateModel(
            name='RepetitionUnit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(verbose_name='Name', max_length=100)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
