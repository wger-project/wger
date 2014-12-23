# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import wger.gym.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminUserNote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp_created', models.DateTimeField(auto_now_add=True)),
                ('timestamp_edited', models.DateTimeField(auto_now=True)),
                ('note', models.TextField(verbose_name='Note')),
                ('member', models.ForeignKey(related_name='adminusernote_member', editable=False, to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='adminusernote_user', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp_created'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Gym',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=60, verbose_name='Name')),
                ('phone', models.CharField(max_length=20, null=True, verbose_name='Phone', blank=True)),
                ('email', models.EmailField(max_length=75, null=True, verbose_name='Email', blank=True)),
                ('owner', models.CharField(max_length=100, null=True, verbose_name='Owner', blank=True)),
                ('zip_code', models.IntegerField(max_length=5, null=True, verbose_name='ZIP code', blank=True)),
                ('city', models.CharField(max_length=30, null=True, verbose_name='City', blank=True)),
                ('street', models.CharField(max_length=30, null=True, verbose_name='Street', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'permissions': (('gym_trainer', 'Trainer, can see the users for a gym'), ('manage_gym', 'Admin, can manage users for a gym'), ('manage_gyms', 'Admin, can administrate the different gyms')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GymAdminConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('overview_inactive', models.BooleanField(default=True, help_text='Receive email overviews of inactive members', verbose_name='Overview inactive members')),
                ('gym', models.ForeignKey(editable=False, to='gym.Gym')),
                ('user', models.OneToOneField(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GymConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weeks_inactive', models.PositiveIntegerField(default=4, help_text='Number of weeks since the last time a user logged his presence to be considered inactive', max_length=2, verbose_name='Reminder inactive members')),
                ('gym', models.OneToOneField(related_name='config', editable=False, to='gym.Gym')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GymUserConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('include_inactive', models.BooleanField(default=True, help_text='Include this user in the email list with inactive members', verbose_name='Include in inactive overview')),
                ('gym', models.ForeignKey(editable=False, to='gym.Gym')),
                ('user', models.OneToOneField(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp_created', models.DateTimeField(auto_now_add=True)),
                ('timestamp_edited', models.DateTimeField(auto_now=True)),
                ('document', models.FileField(upload_to=wger.gym.models.gym_document_upload_dir, verbose_name='Document')),
                ('original_name', models.CharField(max_length=128, editable=False)),
                ('name', models.CharField(help_text='Will use file name if nothing provided', max_length=60, verbose_name='Name', blank=True)),
                ('note', models.TextField(null=True, verbose_name='Note', blank=True)),
                ('member', models.ForeignKey(related_name='userdocument_member', editable=False, to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='userdocument_user', editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp_created'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='gymuserconfig',
            unique_together=set([('gym', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='gymadminconfig',
            unique_together=set([('gym', 'user')]),
        ),
    ]
