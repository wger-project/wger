from pymongo import MongoClient
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
django.setup()
from wger.nutrition.models import Ingredient  # noqa: E402
from wger.core.models import Language  # noqa: E402
from django.utils import timezone  # noqa: E402

client = MongoClient(port=27017)
db = client.off

langs = ["en", "de", "es", "ru", "fr", "bg", "el", "nl", "no", "cs", "sv", "pt"]
lang_objects = [Language.objects.filter(short_name=lang).first() for lang in langs]

for product in db.products.find({'lang': {"$in": langs}}):
    lang = product['lang']

    main_details = ['product_name', 'code']
    if all(req in product for req in main_details):
        name = product['product_name']
        code = product['code']

    required = ['energy-kcal_100g', 'proteins_100g', 'carbohydrates_100g',
                'sugars_100g', 'fat_100g', 'saturated-fat_100g']
    if 'nutriments' in product and all(req in product['nutriments'] for req in required):
        energy = product['nutriments']['energy-kcal_100g']
        protein = product['nutriments']['proteins_100g']
        carbs = product['nutriments']['carbohydrates_100g']
        sugars = product['nutriments']['sugars_100g']
        fat = product['nutriments']['fat_100g']
        saturated = product['nutriments']['saturated-fat_100g']
    else:
        continue

    # these are optional
    sodium = product['nutriments'].get('sodium_100g', None)
    fibre = product['nutriments'].get('fiber_100g', None)
    common_name = product.get('generic_name', None)
    brand = product.get('brands', None)

    source_name = "Open Food Facts"
    source_url = f'https://world.openfoodfacts.org/api/v0/product/{code}.json'

    try:
        Ingredient.objects.create(
            language=lang_objects[langs.index(lang)],
            creation_date=timezone.now(),
            update_date=timezone.now(),
            name=name,
            energy=energy,
            protein=protein,
            carbohydrates=carbs,
            carbohydrates_sugar=sugars,
            fat=fat,
            fat_saturated=saturated,
            fibres=fibre,
            sodium=sodium,
            code=code,
            source_name=source_name,
            source_url=source_url,
            common_name=common_name,
            brand=brand,
            status=2
        )
    except:  # noqa: E722
        continue
