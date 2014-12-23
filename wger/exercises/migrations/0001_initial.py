# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import wger.exercises.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Exercise',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('license_author', models.CharField(help_text='If you are not the author, enter the name or source here. This is needed for some licenses e.g. the CC-BY-SA.', max_length=50, null=True, verbose_name='Author', blank=True)),
                ('status', models.CharField(default=b'1', max_length=2, editable=False, choices=[(b'1', 'Pending'), (b'2', 'Accepted'), (b'3', 'Declined')])),
                ('description', models.TextField(max_length=2000, verbose_name='Description', validators=[django.core.validators.MinLengthValidator(40)])),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('creation_date', models.DateField(auto_now_add=True, verbose_name='Date', null=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExerciseCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'Exercise Categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExerciseComment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.CharField(help_text='A comment about how to correctly do this exercise.', max_length=200, verbose_name='Comment')),
                ('exercise', models.ForeignKey(editable=False, to='exercises.Exercise', verbose_name='Exercise')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExerciseImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('license_author', models.CharField(help_text='If you are not the author, enter the name or source here. This is needed for some licenses e.g. the CC-BY-SA.', max_length=50, null=True, verbose_name='Author', blank=True)),
                ('status', models.CharField(default=b'1', max_length=2, editable=False, choices=[(b'1', 'Pending'), (b'2', 'Accepted'), (b'3', 'Declined')])),
                ('image', models.ImageField(help_text='Only PNG and JPEG formats are supported', upload_to=wger.exercises.models.exercise_image_upload_dir, verbose_name='Image')),
                ('is_main', models.BooleanField(default=False, help_text='Tick the box if you want to set this image as the main one for the exercise (will be shown e.g. in the search). The first image is automatically marked by the system.', verbose_name='Is main picture')),
                ('exercise', models.ForeignKey(verbose_name='Exercise', to='exercises.Exercise')),
                ('license', models.ForeignKey(default=2, verbose_name='License', to='core.License')),
            ],
            options={
                'ordering': ['-is_main', 'id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Muscle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='In latin, e.g. "Pectoralis major"', max_length=50, verbose_name='Name')),
                ('is_front', models.BooleanField(default=1)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='exercise',
            name='category',
            field=models.ForeignKey(verbose_name='Category', to='exercises.ExerciseCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='exercise',
            name='equipment',
            field=models.ManyToManyField(to='exercises.Equipment', null=True, verbose_name='Equipment', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='exercise',
            name='language',
            field=models.ForeignKey(verbose_name='Language', to='core.Language'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='exercise',
            name='license',
            field=models.ForeignKey(default=2, verbose_name='License', to='core.License'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='exercise',
            name='muscles',
            field=models.ManyToManyField(to='exercises.Muscle', null=True, verbose_name='Primary muscles', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='exercise',
            name='muscles_secondary',
            field=models.ManyToManyField(related_name='secondary_muscles', null=True, verbose_name='Secondary muscles', to='exercises.Muscle', blank=True),
            preserve_default=True,
        ),
    ]
