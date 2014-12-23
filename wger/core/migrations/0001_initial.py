# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DaysOfWeek',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('day_of_week', models.CharField(max_length=9, verbose_name='Day of the week')),
            ],
            options={
                'ordering': ['pk'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', models.CharField(max_length=2, verbose_name='Language short name')),
                ('full_name', models.CharField(max_length=30, verbose_name='Language full name')),
            ],
            options={
                'ordering': ['full_name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_name', models.CharField(max_length=60, verbose_name='Full name')),
                ('short_name', models.CharField(max_length=15, verbose_name='Short name, e.g. CC-BY-SA 3')),
                ('url', models.URLField(help_text='Link to license text or other information', null=True, verbose_name='Link', blank=True)),
            ],
            options={
                'ordering': ['full_name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_temporary', models.BooleanField(default=False, editable=False)),
                ('show_comments', models.BooleanField(default=True, help_text='Check to show exercise comments on the workout view', verbose_name='Show exercise comments')),
                ('show_english_ingredients', models.BooleanField(default=True, help_text='Check to also show ingredients in English while creating\na nutritional plan. These ingredients are extracted from a list provided\nby the US Department of Agriculture. It is extremely complete, with around\n7000 entries, but can be somewhat overwhelming and make the search difficult.', verbose_name='Also use ingredients in English')),
                ('workout_reminder_active', models.BooleanField(default=False, help_text='Check to activate automatic reminders for workouts. You need to provide a valid email for this to work.', verbose_name='Activate workout reminders')),
                ('workout_reminder', models.IntegerField(default=14, help_text='The number of days you want to be reminded before a workout expires.', verbose_name='Remind before expiration', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(30)])),
                ('workout_duration', models.IntegerField(default=12, help_text='Default duration in weeks of workouts not in a schedule. Used for email workout reminders.', verbose_name='Default duration of workouts', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(30)])),
                ('last_workout_notification', models.DateField(null=True, editable=False)),
                ('timer_active', models.BooleanField(default=True, help_text='Check to activate timer pauses between exercises.', verbose_name='Use pauses in workout timer')),
                ('timer_pause', models.IntegerField(default=90, help_text='Default duration in seconds of pauses used by the timer in the gym mode.', verbose_name='Default duration of workout pauses', validators=[django.core.validators.MinValueValidator(10), django.core.validators.MaxValueValidator(400)])),
                ('age', models.IntegerField(max_length=2, null=True, verbose_name='Age', validators=[django.core.validators.MinValueValidator(10), django.core.validators.MaxValueValidator(100)])),
                ('height', models.IntegerField(max_length=2, null=True, verbose_name='Height (cm)', validators=[django.core.validators.MinValueValidator(140), django.core.validators.MaxValueValidator(230)])),
                ('gender', models.CharField(default=b'1', max_length=1, null=True, choices=[(b'1', 'Male'), (b'2', 'Female')])),
                ('sleep_hours', models.IntegerField(default=7, help_text='The average hours of sleep per day', null=True, verbose_name='Hours of sleep', validators=[django.core.validators.MinValueValidator(4), django.core.validators.MaxValueValidator(10)])),
                ('work_hours', models.IntegerField(default=8, help_text='Average hours per day', null=True, verbose_name='Work', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(15)])),
                ('work_intensity', models.CharField(default=b'1', choices=[(b'1', 'Low'), (b'2', 'Medium'), (b'3', 'High')], max_length=1, help_text='Approximately', null=True, verbose_name='Physical intensity')),
                ('sport_hours', models.IntegerField(default=3, help_text='Average hours per week', null=True, verbose_name='Sport', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(30)])),
                ('sport_intensity', models.CharField(default=b'2', choices=[(b'1', 'Low'), (b'2', 'Medium'), (b'3', 'High')], max_length=1, help_text='Approximately', null=True, verbose_name='Physical intensity')),
                ('freetime_hours', models.IntegerField(default=8, help_text='Average hours per day', null=True, verbose_name='Free time', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(15)])),
                ('freetime_intensity', models.CharField(default=b'1', choices=[(b'1', 'Low'), (b'2', 'Medium'), (b'3', 'High')], max_length=1, help_text='Approximately', null=True, verbose_name='Physical intensity')),
                ('calories', models.IntegerField(default=2500, help_text='Total caloric intake, including e.g. any surplus', null=True, verbose_name='Total daily calories', validators=[django.core.validators.MinValueValidator(1500), django.core.validators.MaxValueValidator(5000)])),
                ('weight_unit', models.CharField(default=b'kg', max_length=2, verbose_name='Weight unit', choices=[(b'kg', 'Metric (kilogram)'), (b'lb', 'Imperial (pound)')])),
                ('gym', models.ForeignKey(blank=True, editable=False, to='gym.Gym', null=True)),
                ('notification_language', models.ForeignKey(default=2, verbose_name='Notification language', to='core.Language', help_text='Language to use when sending you email notifications, e.g. email reminders for workouts. This does not affect the language used on the website.')),
                ('user', models.OneToOneField(editable=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
