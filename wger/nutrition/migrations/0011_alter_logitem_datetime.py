# Generated by Django 3.2.13 on 2022-05-16 09:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0010_logitem_meal'),
    ]

    operations = [
        migrations.AlterField(
            model_name='logitem',
            name='datetime',
            field=models.DateTimeField(
                default=django.utils.timezone.now, verbose_name='Date and Time (Approx.)'
            ),
        ),
    ]
