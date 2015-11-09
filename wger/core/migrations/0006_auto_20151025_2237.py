# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def create_usercache(apps, schema_editor):
    '''
    Creates a usercache table for all users
    '''
    User = apps.get_model("auth", "User")
    Usercache = apps.get_model("core", "Usercache")
    WorkoutLog = apps.get_model("manager", "WorkoutLog")
    WorkoutSession = apps.get_model("manager", "WorkoutSession")

    for user in User.objects.all():

        #
        # This is the logic of get_user_last_activity at the time this migration
        # was created.
        #
        last_activity = None

        # Check workout logs
        last_log = WorkoutLog.objects.filter(user=user).order_by('date').last()
        if last_log:
            last_activity = last_log.date

        # Check workout sessions
        last_session = WorkoutSession.objects.filter(user=user).order_by('date').last()
        if last_session:
            last_session = last_session.date

        # Return the last one
        if last_session:
            if not last_activity:
                last_activity = last_session

            if last_activity < last_session:
                last_activity = last_session

        # Create the cache entry
        Usercache.objects.create(user=user, last_activity=last_activity)


def delete_usercache(apps, schema_editor):
    '''
    Deletes the usercache table for all users
    '''
    Usercache = apps.get_model("core", "Usercache")
    for cache in Usercache.objects.all():
        cache.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20151025_2236'),
        ('auth', '0006_require_contenttypes_0002'),
        ('manager', '0004_auto_20150609_1603'),
    ]

    operations = [
        migrations.RunPython(create_usercache, delete_usercache)
    ]
