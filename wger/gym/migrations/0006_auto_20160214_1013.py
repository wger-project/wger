
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def update_permission_names(apps, schema_editor):
    '''
    Updates the wording of our three custom gym permissions
    '''
    Permission = apps.get_model("auth", "Permission")

    for name in ['Trainer, can see the users for a gym',
                 'Admin, can manage users for a gym',
                 'Admin, can administrate the different gyms']:

        permission = Permission.objects.get(name=name)
        permission.name = name.replace(',', ':')
        permission.save()


class Migration(migrations.Migration):

    dependencies = [
        ('gym', '0005_auto_20151023_1522'),
    ]

    operations = [
        migrations.RunPython(update_permission_names),
    ]
