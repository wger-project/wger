# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import wger.groups.models


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0002_auto_20150717_2033'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name='Name')),
                ('description', models.TextField(default=b'', verbose_name='Description', blank=True)),
                ('creation_date', models.DateField(auto_now_add=True, verbose_name='Creation date')),
                ('public', models.BooleanField(default=False, help_text='Public groups can be accessed by all users while private groups are invite-only.', verbose_name='Public group')),
                ('image', models.ImageField(help_text='Only PNG and JPEG formats are supported', upload_to=wger.groups.models.group_image_upload_dir, verbose_name='Image')),
                ('gym', models.ForeignKey(blank=True, to='gym.Gym', null=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('admin', models.BooleanField(default=False, verbose_name='Administrator')),
                ('group', models.ForeignKey(to='groups.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='groups.Membership'),
            preserve_default=True,
        ),
    ]
