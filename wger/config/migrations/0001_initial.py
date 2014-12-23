# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GymConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('default_gym', models.ForeignKey(blank=True, to='gym.Gym', help_text='Select the default gym for this installation. This will assign all new registered users to this gym and update all existing users without a gym.', null=True, verbose_name='Default gym')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LanguageConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item', models.CharField(max_length=2, editable=False, choices=[(b'1', 'Exercises'), (b'2', 'Ingredients')])),
                ('show', models.BooleanField(default=1)),
                ('language', models.ForeignKey(related_name='language_source', editable=False, to='core.Language')),
                ('language_target', models.ForeignKey(related_name='language_target', editable=False, to='core.Language')),
            ],
            options={
                'ordering': ['item', 'language_target'],
            },
            bases=(models.Model,),
        ),
    ]
