# Generated by Django 3.2.3 on 2021-09-12 10:31

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('exercises', '0015_auto_20210613_2349'),
    ]

    operations = [
        migrations.AddField(
            model_name='exercisebase',
            name='creation_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Date'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='exercisebase',
            name='update_date',
            field=models.DateTimeField(auto_now=True, verbose_name='Date'),
        ),
        migrations.AddField(
            model_name='historicalexercisebase',
            name='creation_date',
            field=models.DateField(blank=True, default=django.utils.timezone.now, editable=False, verbose_name='Date'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='historicalexercisebase',
            name='update_date',
            field=models.DateTimeField(blank=True, default=django.utils.timezone.now, editable=False, verbose_name='Date'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='exercisecomment',
            name='exercise',
            field=models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to='exercises.exercise', verbose_name='Exercise'),
        ),
        migrations.AlterField(
            model_name='historicalexercisecomment',
            name='exercise',
            field=models.ForeignKey(blank=True, db_constraint=False, editable=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='exercises.exercise', verbose_name='Exercise'),
        ),
    ]