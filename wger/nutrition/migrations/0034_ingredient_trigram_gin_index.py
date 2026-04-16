"""Replace plain GIN index on ingredient name with trigram GIN index.

The existing GIN index (nutrition_i_search__f274b7_gin) does not use
gin_trgm_ops, so it cannot accelerate SIMILARITY() / TrigramSimilarity
queries. This migration drops it and creates a proper trigram index.
"""

import django.contrib.postgres.indexes
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0033_finalize_weight_unit_merge'),
        ('exercises', '0029_full_text_search'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='ingredient',
            name='nutrition_i_search__f274b7_gin',
        ),
        migrations.AddIndex(
            model_name='ingredient',
            index=django.contrib.postgres.indexes.GinIndex(
                fields=['name'],
                name='idx_ingredient_name_trgm',
                opclasses=['gin_trgm_ops'],
            ),
        ),
    ]
