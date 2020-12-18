from pymongo import MongoClient
import os
import django
import sys

sys.path.insert(0, os.path.join('..', '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from django.conf import settings # noqa: E402

from wger.nutrition.models import Ingredient  # noqa: E402
from wger.core.models import Language  # noqa: E402

client = MongoClient(port=27017)
db = client.off

langs = [i[0] for i in settings.LANGUAGES]
lang_objects = [Language.objects.get(short_name=lang) for lang in langs]

# for lang in langs:
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


for product in db.products.find({'lang': {"$in": langs}, 'complete': 1}):
    lang = product['lang']

    main_details = ['product_name', 'code']
    if all(req in product for req in main_details):
        name = product['product_name']
        code = product['code']

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
        continue

    # Some products have no name, skipping
    if not name:
        continue

    print(f'Processing {name}...')

    # these are optional
    sodium = product['nutriments'].get('sodium_100g', None)
    fibre = product['nutriments'].get('fiber_100g', None)
    common_name = product.get('generic_name', None)
    brand = product.get('brands', None)

    source_name = "Open Food Facts"
    source_url = f'https://world.openfoodfacts.org/api/v0/product/{code}.json'

    ingredient_data = {
        'language': lang_objects[langs.index(lang)],
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
    }

    try:
        # Update an existing product (look-up key is the code) or create a new
        # one. While this might not be the most efficient query (there will always
        # be a SELECT first), it's ok because this script is run very rarely.
        obj, created = Ingredient.objects.update_or_create(code=code, defaults=ingredient_data)

        if created:
            print('   -> added to the database')
        else:
            print('   -> updated')

    except:  # noqa: E722
        continue
