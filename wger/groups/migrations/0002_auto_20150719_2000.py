# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import wger.groups.models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='image',
            field=models.ImageField(help_text='Only PNG and JPEG formats are supported', upload_to=wger.groups.models.group_image_upload_dir, null=True, verbose_name='Image', blank=True),
            preserve_default=True,
        ),
    ]
