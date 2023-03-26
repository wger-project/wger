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

from collections import Counter
import enum

from pymongo import MongoClient
import os
import django
import sys

sys.path.insert(0, os.path.join('..', '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from django.conf import settings  # noqa: E402

from wger.nutrition.models import Ingredient  # noqa: E402
from wger.nutrition.models.sources import Source
from wger.core.models import Language  # noqa: E402

"""
Simple script that imports and loads the Open Food Facts database into the
ingredients database.

NOTE: The file is VERY large (40 GB), so it takes a long time (> 3 hours) to
import the data and create all the ingredients.


* Requirements:
 (note that the local mongo version needs to be compatible with the one used to
 create the dump, otherwise the indices won't be compatible, it is best to use
 a newer version than the one found in the ubuntu/debian repos)

 - MongoDB
 https://www.mongodb.com/docs/manual/tutorial/install-mongodb-on-ubuntu/

 - Docker
 snap install docker

pip3 install pymongo
apt-get install mongo-tools zip

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
python3 filter-fixtures.py
zip ingredients.json.zip ingredients.json
"""

client = MongoClient('mongodb://off:off-wger@127.0.0.1', port=27017)
db = client.admin


# Mode for this script. When using 'insert', the script will bulk-insert the new
# ingredients, which is very efficient. Importing the whole database will require
# barely a minute. When using 'update', existing ingredients will be updated, which
# requires two queries per product.
class Mode(enum.Enum):
    INSERT = enum.auto()
    UPDATE = enum.auto()


MODE = Mode.UPDATE

languages = {l.short_name: l for l in Language.objects.all()}

BULK_SIZE = 500
bulk_update_bucket = []
counter = Counter()

# for lang in languages.keys():
#    count = db.products.count_documents({'lang': lang, 'complete': 1})
#    total = db.products.count_documents({'lang': lang})
#    print(f'Lang {lang} has {count} completed products out of {total}')

# Completeness status of ingredients as of 2021-11-18
#
# Lang az has 0 completed products out of 39
# Lang id has 6 completed products out of 845
# Lang cs has 78 completed products out of 3736
# Lang de has 972 completed products out of 157846
# Lang en has 959 completed products out of 905683
# Lang es has 533 completed products out of 300344
# Lang eo has 0 completed products out of 9
# Lang fr has 6677 completed products out of 1145075
# Lang hr has 56 completed products out of 1544
# Lang it has 809 completed products out of 211901
# Lang nl has 71 completed products out of 11202
# Lang no has 4 completed products out of 247
# Lang pl has 45 completed products out of 6793
# Lang pt has 132 completed products out of 9427
# Lang sv has 297 completed products out of 4501
# Lang tr has 3 completed products out of 1209
# Lang el has 6 completed products out of 880
# Lang bg has 31 completed products out of 3392
# Lang ru has 13 completed products out of 10799
# Lang uk has 1 completed products out of 297
# Lang he has 0 completed products out of 352
# Lang ar has 1 completed products out of 3426
# Lang fa has 0 completed products out of 577
# Lang zh has 2 completed products out of 913

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
        counter['skipped'] += 1
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
        counter['skipped'] += 1
        continue

    # these are optional
    sodium = product['nutriments'].get('sodium_100g', None)
    fibre = product['nutriments'].get('fiber_100g', None)
    common_name = product.get('generic_name', None)
    brand = product.get('brands', None)

    if common_name and len(common_name) > 200:
        continue

    source_name = Source.OPEN_FOOD_FACTS.value
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
        'license_author': Source.OPEN_FOOD_FACTS.value,
    }

    # Add entries as new products
    if MODE == Mode.INSERT:
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
                    except Exception as e:
                        print('--> Error while saving the product individually')
                        print(e)

            counter['new'] += BULK_SIZE
            bulk_update_bucket = []

    # Update existing entries
    else:
        try:

            # Update an existing product (look-up key is the code) or create a new
            # one. While this might not be the most efficient query (there will always
            # be a SELECT first), it's ok because this script is run very rarely.
            obj, created = Ingredient.objects.update_or_create(code=code, defaults=ingredient_data)

            if created:
                counter['new'] += 1
                # print('-> added to the database')
            else:
                counter['edited'] += 1
                # print('-> updated')

        except Exception as e:
            print('--> Error while performing update_or_create')
            print(e)
            continue

print('***********************************')
print(counter)
print('***********************************')
