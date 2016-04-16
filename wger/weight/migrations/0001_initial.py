# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WeightEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateField(verbose_name='Date')),
                ('weight', models.DecimalField(verbose_name='Weight', max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(30), django.core.validators.MaxValueValidator(300)])),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['creation_date'],
                'get_latest_by': 'creation_date',
                'verbose_name': 'Weight entry',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='weightentry',
            unique_together=set([('creation_date', 'user')]),
        ),
    ]
