# -*- coding: utf-8 -*-

from django.db import migrations


class Migration(migrations.Migration):
    """
    Originally converted Set.exercises to a django-sortedm2m field. That field
    was removed in 0011_remove_set_exercises, so this is now a no-op to drop
    the dependency on django-sortedm2m.
    """

    dependencies = [
        ('manager', '0001_initial'),
    ]

    operations = []
