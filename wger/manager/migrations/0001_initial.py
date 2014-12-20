# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wger.utils.fields
import datetime
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('exercises', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Day',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(help_text='Ususally a description about what parts are trained, like "Arms" or "Pull Day"', max_length=100, verbose_name='Description')),
                ('day', models.ManyToManyField(to='core.DaysOfWeek', verbose_name='Day')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text="Name or short description of the schedule. For example 'Program XYZ'.", max_length=100, verbose_name='Name')),
                ('start_date', wger.utils.fields.Html5DateField(default=datetime.date.today, verbose_name='Start date')),
                ('is_active', models.BooleanField(default=True, help_text='Tick the box if you want to mark this schedule as your active one (will be shown e.g. on your dashboard). All other schedules will then be marked as inactive', verbose_name='Schedule active')),
                ('is_loop', models.BooleanField(default=False, help_text='Tick the box if you want to repeat the schedules in a loop (i.e. A, B, C, A, B, C, and so on)', verbose_name='Is loop')),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ScheduleStep',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('duration', models.IntegerField(default=4, help_text='The duration in weeks', verbose_name='Duration', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(25)])),
                ('order', models.IntegerField(default=1, max_length=1, verbose_name='Order')),
                ('schedule', models.ForeignKey(verbose_name='schedule', to='manager.Schedule')),
            ],
            options={
                'ordering': ['order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('order', models.IntegerField(null=True, verbose_name='Order', blank=True)),
                ('sets', models.IntegerField(default=4, verbose_name='Number of sets', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)])),
                ('exerciseday', models.ForeignKey(verbose_name='Exercise day', to='manager.Day')),
                ('exercises', models.ManyToManyField(to='exercises.Exercise', verbose_name='Exercises')),
            ],
            options={
                'ordering': ['order'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Setting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reps', models.IntegerField(verbose_name='Repetitions', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('order', models.IntegerField(verbose_name='Order', blank=True)),
                ('comment', models.CharField(max_length=100, verbose_name='Comment', blank=True)),
                ('exercise', models.ForeignKey(verbose_name='Exercises', to='exercises.Exercise')),
                ('set', models.ForeignKey(verbose_name='Sets', to='manager.Set')),
            ],
            options={
                'ordering': ['order', 'id'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('creation_date', models.DateField(auto_now_add=True, verbose_name='Creation date')),
                ('comment', models.CharField(help_text="A short description or goal of the workout. For example 'Focus on back' or 'Week 1 of program xy'.", max_length=100, verbose_name='Description', blank=True)),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-creation_date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WorkoutLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reps', models.IntegerField(verbose_name='Repetitions', validators=[django.core.validators.MinValueValidator(0)])),
                ('weight', models.DecimalField(verbose_name='Weight', max_digits=5, decimal_places=2, validators=[django.core.validators.MinValueValidator(0)])),
                ('date', wger.utils.fields.Html5DateField(verbose_name='Date')),
                ('exercise', models.ForeignKey(verbose_name='Exercise', to='exercises.Exercise')),
                ('user', models.ForeignKey(editable=False, to=settings.AUTH_USER_MODEL, verbose_name='User')),
                ('workout', models.ForeignKey(verbose_name='Workout', to='manager.Workout')),
            ],
            options={
                'ordering': ['date', 'reps'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='WorkoutSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', wger.utils.fields.Html5DateField(verbose_name='Date')),
                ('notes', models.TextField(help_text='Any notes you might want to save about this workout session.', null=True, verbose_name='Notes', blank=True)),
                ('impression', models.CharField(default=b'2', help_text='Your impression about this workout session. Did you exercise as well as you could?', max_length=2, verbose_name='General impression', choices=[(b'1', 'Bad'), (b'2', 'Neutral'), (b'3', 'Good')])),
                ('time_start', models.TimeField(null=True, verbose_name='Start time', blank=True)),
                ('time_end', models.TimeField(null=True, verbose_name='Finish time', blank=True)),
                ('user', models.ForeignKey(verbose_name='User', to=settings.AUTH_USER_MODEL)),
                ('workout', models.ForeignKey(verbose_name='Workout', to='manager.Workout')),
            ],
            options={
                'ordering': ['date'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='workoutsession',
            unique_together=set([('date', 'user')]),
        ),
        migrations.AddField(
            model_name='schedulestep',
            name='workout',
            field=models.ForeignKey(to='manager.Workout'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='day',
            name='training',
            field=models.ForeignKey(verbose_name='Workout', to='manager.Workout'),
            preserve_default=True,
        ),
    ]
