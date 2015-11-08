# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gym', '0002_auto_20151003_1944'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('timestamp_created', models.DateTimeField(auto_now_add=True)),
                ('timestamp_edited', models.DateTimeField(auto_now=True)),
                ('amount', models.PositiveIntegerField(verbose_name='Amount', default=0)),
                ('payment', models.CharField(verbose_name='Payment type', default='3', help_text='How often the amount will be charged to the member', choices=[('1', 'Yearly'), ('2', 'Half yearly'), ('3', 'Monthly'), ('4', 'Biweekly'), ('5', 'Weekly'), ('6', 'Daily')], max_length=2)),
                ('is_active', models.BooleanField(verbose_name='Contract is active', default=True)),
                ('date_start', models.DateField(verbose_name='Start date', blank=True, default=datetime.date.today, null=True)),
                ('date_end', models.DateField(verbose_name='End date', blank=True, null=True)),
                ('email', models.EmailField(verbose_name='Email', blank=True, null=True, max_length=254)),
                ('zip_code', models.CharField(verbose_name='ZIP code', blank=True, null=True, max_length=10)),
                ('city', models.CharField(verbose_name='City', blank=True, null=True, max_length=30)),
                ('street', models.CharField(verbose_name='Street', blank=True, null=True, max_length=30)),
                ('phone', models.CharField(verbose_name='Phone', blank=True, null=True, max_length=20)),
                ('profession', models.CharField(verbose_name='Profession', blank=True, null=True, max_length=50)),
                ('note', models.TextField(verbose_name='Note', blank=True, null=True)),
            ],
            options={
                'ordering': ['-date_start'],
            },
        ),
        migrations.CreateModel(
            name='ContractType',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=25)),
                ('description', models.TextField(verbose_name='Description', blank=True, null=True)),
                ('gym', models.ForeignKey(to='gym.Gym', editable=False)),
            ],
        ),
        migrations.AddField(
            model_name='contract',
            name='contract_type',
            field=models.ForeignKey(verbose_name='Contract type', blank=True, null=True, to='gym.ContractType'),
        ),
        migrations.AddField(
            model_name='contract',
            name='member',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, related_name='contract_member'),
        ),
        migrations.AddField(
            model_name='contract',
            name='user',
            field=models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, related_name='contract_user'),
        ),
    ]
