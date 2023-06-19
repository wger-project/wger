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

from wger.nutrition.models.off import extract_info_from_off

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
# import sys
# sys.exit()

# Completeness status of ingredients as of 2023-04-08
#
# Lang az has 0 completed products out of 40
# Lang id has 6 completed products out of 981
# Lang cs has 80 completed products out of 4654
# Lang de has 1025 completed products out of 165771
# Lang en has 1028 completed products out of 929003
# Lang es has 618 completed products out of 303937
# Lang eo has 0 completed products out of 9
# Lang fr has 7125 completed products out of 1160796
# Lang hr has 57 completed products out of 1699
# Lang it has 870 completed products out of 216046
# Lang nl has 71 completed products out of 11744
# Lang no has 4 completed products out of 261
# Lang pl has 48 completed products out of 7145
# Lang pt has 127 completed products out of 9802
# Lang sv has 308 completed products out of 4622
# Lang tr has 3 completed products out of 1296
# Lang el has 6 completed products out of 927
# Lang bg has 31 completed products out of 4524
# Lang ru has 23 completed products out of 11683
# Lang uk has 2 completed products out of 604
# Lang he has 0 completed products out of 365
# Lang ar has 1 completed products out of 3552
# Lang fa has 0 completed products out of 575
# Lang zh has 2 completed products out of 935

print('***********************************')
print(languages.keys())
print('***********************************')

for product in db.products.find({'lang': {"$in": list(languages.keys())}, 'complete': 1}):

    try:
        ingredient_data = extract_info_from_off(product, languages[product['lang']])
    except KeyError as e:
        # print('--> KeyError while extracting info from OFF', e)
        counter['skipped'] += 1
        continue

    # Some products have no name or name is too long, skipping
    if not ingredient_data['name']:
        counter['skipped'] += 1
        continue

    if not ingredient_data['common_name']:
        counter['skipped'] += 1
        continue

    #
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
            obj, created = Ingredient.objects.update_or_create(
                code=ingredient_data['code'],
                defaults=ingredient_data
            )

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
