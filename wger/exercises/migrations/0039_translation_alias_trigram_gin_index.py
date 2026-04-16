"""Replace plain GIN indexes on translation name and alias with trigram GIN indexes.

The existing GIN indexes do not use gin_trgm_ops, so they cannot accelerate
the % operator used by trigram_similar lookups. This migration replaces them
with proper trigram indexes.
"""

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('exercises', '0038_sync_model_changes'),
    ]

    operations = [
        # Translation.name
        migrations.RemoveIndex(
            model_name='translation',
            name='exercises_e_name_ac11f4_gin',
        ),
        migrations.AddIndex(
            model_name='translation',
            index=django.contrib.postgres.indexes.GinIndex(
                fields=['name'],
                name='idx_translation_name_trgm',
                opclasses=['gin_trgm_ops'],
            ),
        ),
        # Alias.alias
        migrations.RemoveIndex(
            model_name='alias',
            name='exercises_a_alias_227e38_gin',
        ),
        migrations.AddIndex(
            model_name='alias',
            index=django.contrib.postgres.indexes.GinIndex(
                fields=['alias'],
                name='idx_alias_alias_trgm',
                opclasses=['gin_trgm_ops'],
            ),
        ),
    ]
