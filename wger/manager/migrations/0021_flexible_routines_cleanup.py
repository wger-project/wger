# Generated by Django 4.2.13 on 2024-06-12 12:59

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('manager', '0019_flexible_routines_migration'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workoutlog',
            name='workout',
        ),
        migrations.RemoveField(
            model_name='workoutsession',
            name='workout',
        ),
        migrations.RenameField(
            model_name='workoutlog',
            old_name='exercise_base',
            new_name='exercise',
        ),
        migrations.DeleteModel(
            name='Setting',
        ),
        migrations.DeleteModel(
            name='Set',
        ),
        migrations.DeleteModel(
            name='Day',
        ),
        migrations.DeleteModel(
            name='Workout',
        ),
        migrations.DeleteModel(
            name='Schedule',
        ),
        migrations.DeleteModel(
            name='ScheduleStep',
        ),
        migrations.RenameModel(
            old_name='DayNg',
            new_name='Day',
        ),
    ]
