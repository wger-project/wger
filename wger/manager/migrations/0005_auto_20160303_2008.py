# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_repetitionunit'),
        ('manager', '0004_auto_20150609_1603'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='unit',
            field=models.ForeignKey(verbose_name='Unit', default=1, to='core.RepetitionUnit'),
        ),
        migrations.AddField(
            model_name='workoutlog',
            name='unit',
            field=models.ForeignKey(verbose_name='Unit', default=1, to='core.RepetitionUnit'),
        ),
        migrations.AlterField(
            model_name='day',
            name='description',
            field=models.CharField(verbose_name='Description', help_text='A description of what is done on this day (e.g. "Pull day") or what body parts are trained (e.g. "Arms and abs")', max_length=100),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='is_loop',
            field=models.BooleanField(verbose_name='Is a loop', default=False, help_text='Tick the box if you want to repeat the schedules in a loop (i.e. A, B, C, A, B, C, and so on)'),
        ),
        migrations.AlterField(
            model_name='schedulestep',
            name='order',
            field=models.IntegerField(verbose_name='Order', default=1),
        ),
        migrations.AlterField(
            model_name='setting',
            name='reps',
            field=models.IntegerField(verbose_name='Amount', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='workoutsession',
            name='impression',
            field=models.CharField(verbose_name='General impression', default='2', choices=[('1', 'Bad'), ('2', 'Neutral'), ('3', 'Good')], help_text='Your impression about this workout session. Did you exercise as well as you could?', max_length=2),
        ),
    ]
