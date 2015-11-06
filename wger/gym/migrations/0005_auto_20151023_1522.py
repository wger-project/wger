# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0004_auto_20151003_2357'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContractOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25, verbose_name='Name')),
                ('description', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('gym', models.ForeignKey(editable=False, to='gym.Gym')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='contracttype',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='contract',
            name='options',
            field=models.ManyToManyField(to='gym.ContractOption', verbose_name='Options'),
        ),
    ]
