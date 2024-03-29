# Generated by Django 3.2.3 on 2021-07-17 16:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('manager', '0013_set_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='workout',
            name='is_public',
            field=models.BooleanField(default=False, help_text='', verbose_name='Public Template'),
        ),
        migrations.AddField(
            model_name='workout',
            name='is_template',
            field=models.BooleanField(default=False, help_text='', verbose_name='Workout Template'),
        ),
    ]
