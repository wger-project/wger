# Generated by Django 3.2.3 on 2021-06-08 22:48

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0012_auto_20210210_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
    ]
