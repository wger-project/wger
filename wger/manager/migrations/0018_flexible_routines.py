# Generated by Django 4.2.6 on 2024-03-12 15:17

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0016_alter_language_short_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('exercises', '0028_add_uuid_alias_and_comments'),
        ('manager', '0017_alter_workoutlog_exercise_base'),
    ]

    operations = [
        migrations.CreateModel(
            name='DayNg',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('description', models.CharField(max_length=50, verbose_name='Description')),
                ('is_rest', models.BooleanField(default=False)),
                ('need_logs_to_advance', models.BooleanField(default=False)),
                (
                    'next_day',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to='manager.dayng',
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name='SetConfig',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('order', models.PositiveIntegerField(blank=True)),
                ('comment', models.CharField(blank=True, max_length=100)),
                ('class_name', models.CharField(blank=True, max_length=100, null=True)),
                (
                    'exercise',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='exercises.exercisebase'
                    ),
                ),
                (
                    'repetition_unit',
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        to='core.repetitionunit',
                    ),
                ),
                (
                    'set',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='manager.set',
                        verbose_name='Sets',
                    ),
                ),
                (
                    'weight_unit',
                    models.ForeignKey(
                        default=1,
                        on_delete=django.db.models.deletion.CASCADE,
                        to='core.weightunit',
                        verbose_name='Unit',
                    ),
                ),
            ],
            options={
                'ordering': ['order', 'id'],
            },
        ),
        migrations.AddField(
            model_name='workoutlog',
            name='iteration',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AddField(
            model_name='workoutlog',
            name='session',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='manager.workoutsession',
                verbose_name='Session',
            ),
        ),
        migrations.AlterField(
            model_name='workoutlog',
            name='date',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='Date'),
        ),
        migrations.AlterField(
            model_name='workoutsession',
            name='date',
            field=models.DateField(default=datetime.date.today, verbose_name='Date'),
        ),
        migrations.CreateModel(
            name='SetNg',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('order', models.IntegerField(default=1, verbose_name='Order')),
                ('comment', models.CharField(blank=True, max_length=200, verbose_name='Comment')),
                ('is_dropset', models.BooleanField(default=False)),
                (
                    'day',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='manager.day',
                        verbose_name='Exercise day',
                    ),
                ),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Routine',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('name', models.CharField(blank=True, max_length=50, verbose_name='Name')),
                (
                    'description',
                    models.TextField(blank=True, max_length=1000, verbose_name='Description'),
                ),
                (
                    'creation_date',
                    models.DateTimeField(auto_now_add=True, verbose_name='Creation date'),
                ),
                ('start', models.DateField(verbose_name='Start date')),
                ('end', models.DateField(verbose_name='End date')),
                (
                    'first_day',
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='day',
                        to='manager.dayng',
                    ),
                ),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name='User',
                    ),
                ),
            ],
            options={
                'ordering': ['-creation_date'],
            },
        ),
        migrations.AddField(
            model_name='dayng',
            name='routine',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='manager.routine',
                verbose_name='Routine',
            ),
        ),
        migrations.AddField(
            model_name='workoutlog',
            name='set_config',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to='manager.setconfig'
            ),
        ),
        migrations.AddField(
            model_name='workoutsession',
            name='day',
            field=models.ForeignKey(
                null=True, on_delete=django.db.models.deletion.CASCADE, to='manager.dayng'
            ),
        ),
        migrations.CreateModel(
            name='WeightConfig',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('iteration', models.PositiveIntegerField()),
                (
                    'trigger',
                    models.CharField(
                        choices=[('session', 'Session'), ('week', 'Week')],
                        default='session',
                        max_length=10,
                        null=True,
                    ),
                ),
                ('value', models.DecimalField(decimal_places=2, max_digits=6)),
                (
                    'operation',
                    models.CharField(
                        choices=[('+', 'Plus'), ('-', 'Minus')],
                        default='+',
                        max_length=1,
                        null=True,
                    ),
                ),
                (
                    'step',
                    models.CharField(
                        choices=[('abs', 'Absolute'), ('percent', 'Percent')],
                        default='abs',
                        max_length=10,
                        null=True,
                    ),
                ),
                ('replace', models.BooleanField(default=False)),
                ('need_log_to_apply', models.BooleanField(default=False)),
                (
                    'set_config',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='manager.setconfig'
                    ),
                ),
            ],
            options={
                'ordering': ['set_config', 'iteration'],
                'abstract': False,
                'unique_together': {('set_config', 'iteration')},
            },
        ),
        migrations.CreateModel(
            name='RiRConfig',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('iteration', models.PositiveIntegerField()),
                (
                    'trigger',
                    models.CharField(
                        choices=[('session', 'Session'), ('week', 'Week')],
                        default='session',
                        max_length=10,
                        null=True,
                    ),
                ),
                ('value', models.DecimalField(decimal_places=2, max_digits=6)),
                (
                    'operation',
                    models.CharField(
                        choices=[('+', 'Plus'), ('-', 'Minus')],
                        default='+',
                        max_length=1,
                        null=True,
                    ),
                ),
                (
                    'step',
                    models.CharField(
                        choices=[('abs', 'Absolute'), ('percent', 'Percent')],
                        default='abs',
                        max_length=10,
                        null=True,
                    ),
                ),
                ('replace', models.BooleanField(default=False)),
                ('need_log_to_apply', models.BooleanField(default=False)),
                (
                    'set_config',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='manager.setconfig'
                    ),
                ),
            ],
            options={
                'ordering': ['set_config', 'iteration'],
                'abstract': False,
                'unique_together': {('set_config', 'iteration')},
            },
        ),
        migrations.CreateModel(
            name='RestConfig',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('iteration', models.PositiveIntegerField()),
                (
                    'trigger',
                    models.CharField(
                        choices=[('session', 'Session'), ('week', 'Week')],
                        default='session',
                        max_length=10,
                        null=True,
                    ),
                ),
                ('value', models.DecimalField(decimal_places=2, max_digits=6)),
                (
                    'operation',
                    models.CharField(
                        choices=[('+', 'Plus'), ('-', 'Minus')],
                        default='+',
                        max_length=1,
                        null=True,
                    ),
                ),
                (
                    'step',
                    models.CharField(
                        choices=[('abs', 'Absolute'), ('percent', 'Percent')],
                        default='abs',
                        max_length=10,
                        null=True,
                    ),
                ),
                ('replace', models.BooleanField(default=False)),
                ('need_log_to_apply', models.BooleanField(default=False)),
                (
                    'set_config',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='manager.setconfig'
                    ),
                ),
            ],
            options={
                'ordering': ['set_config', 'iteration'],
                'abstract': False,
                'unique_together': {('set_config', 'iteration')},
            },
        ),
        migrations.CreateModel(
            name='RepsConfig',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('iteration', models.PositiveIntegerField()),
                (
                    'trigger',
                    models.CharField(
                        choices=[('session', 'Session'), ('week', 'Week')],
                        default='session',
                        max_length=10,
                        null=True,
                    ),
                ),
                ('value', models.DecimalField(decimal_places=2, max_digits=6)),
                (
                    'operation',
                    models.CharField(
                        choices=[('+', 'Plus'), ('-', 'Minus')],
                        default='+',
                        max_length=1,
                        null=True,
                    ),
                ),
                (
                    'step',
                    models.CharField(
                        choices=[('abs', 'Absolute'), ('percent', 'Percent')],
                        default='abs',
                        max_length=10,
                        null=True,
                    ),
                ),
                ('replace', models.BooleanField(default=False)),
                ('need_log_to_apply', models.BooleanField(default=False)),
                (
                    'set_config',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='manager.setconfig'
                    ),
                ),
            ],
            options={
                'ordering': ['set_config', 'iteration'],
                'abstract': False,
                'unique_together': {('set_config', 'iteration')},
            },
        ),
    ]
