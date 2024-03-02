# -*- coding: utf-8 -*-

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        ('gym', '0004_auto_20151003_2357'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CronEntry',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                (
                    'id',
                    models.AutoField(
                        verbose_name='ID', serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ('date', models.DateField(auto_now=True)),
                ('subject', models.CharField(max_length=100)),
                ('body', models.TextField()),
                ('gym', models.ForeignKey(editable=False, to='gym.Gym', on_delete=models.CASCADE)),
                (
                    'user',
                    models.ForeignKey(
                        editable=False, to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name='cronentry',
            name='log',
            field=models.ForeignKey(editable=False, to='mailer.Log', on_delete=models.CASCADE),
        ),
    ]
