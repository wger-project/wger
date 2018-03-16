# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('config', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCanCreate',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True,
                                        serialize=False,
                                        verbose_name='ID')),
                ('ingredient_perm', models.CharField(choices=[('DENY', 'DENY - user cannot create new items'),
                                                              ('REVIEW', 'REVIEW - user may submit item for approval'),
                                                              ('ACCEPT', 'ACCEPT - user can create items without approval')],
                                                     default='REVIEW', help_text='Allow user to submit new ingredient',
                                                     max_length=6,
                                                     verbose_name='Allow user to submit new ingredient')
                 ),
                ('exercise_perm', models.CharField(choices=[('DENY', 'DENY - user cannot create new items'),
                                                            ('REVIEW', 'REVIEW - user may submit item for approval'),
                                                            ('ACCEPT', 'ACCEPT - user can create items without approval')],
                                                   default='REVIEW', help_text='Allow user to submit new exercise',
                                                   max_length=6, verbose_name='Allow user to submit new exercise')
                 ),
                ('user', models.OneToOneField(editable=False,
                                              on_delete=django.db.models.deletion.CASCADE,
                                              to=settings.AUTH_USER_MODEL)
                 ),
            ],
        ),
        migrations.AlterField(
            model_name='languageconfig',
            name='item',
            field=models.CharField(choices=[('1', 'Exercises'),
                                            ('2', 'Ingredients')],
                                   editable=False,
                                   max_length=2),
        ),
    ]
