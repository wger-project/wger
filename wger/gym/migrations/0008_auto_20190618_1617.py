# -*- coding: utf-8 -*-

# Generated by Django 1.11.21 on 2019-06-18 16:17
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('gym', '0007_auto_20170123_0920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gymconfig',
            name='show_name',
            field=models.BooleanField(
                default=False,
                help_text='Show the name of the gym in the site header',
                verbose_name='Show name in header',
            ),
        ),
    ]
