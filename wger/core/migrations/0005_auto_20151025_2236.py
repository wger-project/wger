# -*- coding: utf-8 -*-
# flake8: noqa
from django.db import migrations, models
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0004_auto_20150217_1914'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCache',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_activity', models.DateField(null=True)),
                ('user', models.OneToOneField(editable=False, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='num_days_weight_reminder',
            field=models.IntegerField(default=0, verbose_name='Automatic reminders for weight entries', help_text='Number of days after the last weight entry (enter 0 to deactivate)', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(30)]),
        ),
    ]
