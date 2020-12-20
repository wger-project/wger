# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

from pymongo import MongoClient
import os
import django
import sys

sys.path.insert(0, os.path.join('..', '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from django.conf import settings  # noqa: E402

from wger.nutrition.models import Ingredient  # noqa: E402
from wger.core.models import Language  # noqa: E402


"""
Simple script that imports and loads the Open Food Facts database into the
ingredients database.

NOTE: The file is VERY large (17 GB), so it takes a long time (> 3 hours) to run
and create all ingredients.


* Requirements:
pip3 install pymongo zip
apt-get install mongo-tools  # (for mongorestore)

* Steps:
wget https://static.openfoodfacts.org/data/openfoodfacts-mongodbdump.tar.gz
tar xzvf openfoodfacts-mongodbdump.tar.gz

# Import
docker pull mongo
docker run -it --name wger_mongo -p 27017:27017 -d  \
    -e MONGO_INITDB_ROOT_USERNAME=off \
    -e MONGO_INITDB_ROOT_PASSWORD=off-wger \
    mongo:latest
mongorestore --username off --password off-wger -d admin -c products dump/off/products.bson

# Process
python extras/scripts/create_ingredients_from_foodfacts.py

# Cleanup
docker stop wger_mongo
docker rm wger_mongo
rm openfoodfacts-mongodbdump.tar.gz
rm -r dump

# Update ingredient fixture
python3 manage.py dumpdata nutrition.ingredient > extras/scripts/data.json
cd extras/scripts/
python3 python3 filter-fixtures.py
zip ingredients.json.zip ingredients.json
"""


client = MongoClient('mongodb://off:off-wger@127.0.0.1', port=27017)
db = client.admin

# Mode for this script. When using 'insert', the script will bulk-insert the new
# ingredients, which is very efficient. Importing the whole database will require
# barely a minute. When using 'update', existing ingredients will be updated, which
# requires two queries per product.
MODE = 'insert'

languages = {i[0]: Language.objects.get(short_name=i[0]) for i in settings.LANGUAGES}

BULK_SIZE = 500
bulk_update_bucket = []
stats = {'new': 0,
         'edited': 0,
         'skipped': 0}

# for lang in languages.keys():
#    count = db.products.count_documents({'lang': lang, 'complete': 1})
#    total = db.products.count_documents({'lang': lang})
#    print(f'Lang {lang} has {count} completed products out of {total}')

# Lang de has 15667 completed products out of 52669
# Lang es has 8757 completed products out of 186171
# Lang ru has 505 completed products out of 2918
# Lang fr has 85058 completed products out of 811715
# Lang bg has 15 completed products out of 718
# Lang el has 20 completed products out of 251
# Lang nl has 750 completed products out of 5611
# Lang no has 9 completed products out of 141
# Lang cs has 123 completed products out of 789
# Lang sv has 1340 completed products out of 2878
# Lang pt has 526 completed products out of 3541

print('***********************************')
print(languages.keys())
print('***********************************')


for product in db.products.find({'lang': {"$in": list(languages.keys())}, 'complete': 1}):
    lang = product['lang']

    main_details = ['product_name', 'code']
    if all(req in product for req in main_details):
        name = product['product_name']
        code = product['code']

    # Some products have no name or name is too long, skipping
    if not name or len(name) > 200:
        # print(f'-> skipping due to name requirements')
        stats['skipped'] += 1
        continue

    # print(f'Processing "{name}"...')

    required = ['energy-kcal_100g',
                'proteins_100g',
                'carbohydrates_100g',
                'sugars_100g',
                'fat_100g',
                'saturated-fat_100g']
    if 'nutriments' in product and all(req in product['nutriments'] for req in required):
        energy = product['nutriments']['energy-kcal_100g']
        protein = product['nutriments']['proteins_100g']
        carbs = product['nutriments']['carbohydrates_100g']
        sugars = product['nutriments']['sugars_100g']
        fat = product['nutriments']['fat_100g']
        saturated = product['nutriments']['saturated-fat_100g']
    else:
        # print(f'-> skipping due to required nutriments')
        stats['skipped'] += 1
        continue

    # these are optional
    sodium = product['nutriments'].get('sodium_100g', None)
    fibre = product['nutriments'].get('fiber_100g', None)
    common_name = product.get('generic_name', None)
    brand = product.get('brands', None)

    if common_name and len(common_name) > 200:
        continue

    source_name = "Open Food Facts"
    source_url = f'https://world.openfoodfacts.org/api/v0/product/{code}.json'

    ingredient_data = {
        'language': languages[lang],
        'name': name,
        'energy': energy,
        'protein': protein,
        'carbohydrates': carbs,
        'carbohydrates_sugar': sugars,
        'fat': fat,
        'fat_saturated': saturated,
        'fibres': fibre,
        'sodium': sodium,
        'code': code,
        'source_name': source_name,
        'source_url': source_url,
        'common_name': common_name,
        'brand': brand,
        'status': 2,
        'license_id': 5,
        'license_author': 'Open Food Facts',
    }

    # Add entries as new products
    if MODE == 'insert':
        bulk_update_bucket.append(Ingredient(**ingredient_data))
        if len(bulk_update_bucket) > BULK_SIZE:
            try:
                Ingredient.objects.bulk_create(bulk_update_bucket)
                print('***** Bulk adding products *****')
            except Exception as e:
                print('--> Error while saving the product bucket. Saving individually')
                print(e)

                # Try saving the ingredients individually as most will be correct
                for ingredient in bulk_update_bucket:
                    try:
                        ingredient.save()

                    # ¯\_(ツ)_/¯
                    except Exception:
                        pass

            stats['new'] += BULK_SIZE
            bulk_update_bucket = []

    # Update existing entries
    else:
        try:

            # Update an existing product (look-up key is the code) or create a new
            # one. While this might not be the most efficient query (there will always
            # be a SELECT first), it's ok because this script is run very rarely.
            obj, created = Ingredient.objects.update_or_create(code=code, defaults=ingredient_data)

            if created:
                stats['new'] += 1
                # print('-> added to the database')
            else:
                stats['edited'] += 1
                # print('-> updated')

        except:  # noqa: E722
            continue

print('***********************************')
print(stats)
print('***********************************')
