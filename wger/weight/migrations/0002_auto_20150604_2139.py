# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('weight', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='weightentry',
            options={'verbose_name': 'Weight entry', 'get_latest_by': 'date', 'ordering': ['date']},
        ),
        migrations.RenameField(
            model_name='weightentry',
            old_name='creation_date',
            new_name='date',
        ),
        migrations.AlterUniqueTogether(
            name='weightentry',
            unique_together=set([('date', 'user')]),
        ),
    ]
