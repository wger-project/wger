from pymongo import MongoClient
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import django
django.setup()
from wger.nutrition.models import Ingredient
from wger.core.models import Language
from django.utils import timezone

client = MongoClient(port=27017)
db = client.off

langs = {"en": "English", "de": "German", "es": "Spanish", 
        "ru": "Russian", "fr": "French", "bg": "Bulgarian", 
        "el": "Greek", "nl": "Dutch", "no": "Norwegian", "cs": "Czech",
        "sv": "Swedish", "pt": "Portuguese"}

for product in db.products.find({'lang': { "$in": list(langs.keys())}}):
    lang = product['lang']

    main_details = ['product_name', 'code']
    if all(req in product for req in main_details):
        name = product['product_name']
        code = product['code']

    required = ['energy-kcal_100g', 'proteins_100g', 'carbohydrates_100g', 
        'sugars_100g', 'fat_100g', 'saturated-fat_100g']
    if all(req in product['nutriments'] for req in required):
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
    
    lang_object = Language.objects.create(
        short_name = lang,
        full_name = langs[lang]
    )

    Ingredient.objects.create(
        language = lang_object,
        creation_date = timezone.now(),
        update_date = timezone.now(),
        name = name,
        energy = energy,
        protein = protein,
        carbohydrates = carbs,
        carbohydrates_sugar = sugars,
        fat = fat,
        fat_saturated = saturated,
        fibres = fibre,
        sodium = sodium,
        code = code,
        source_name = source_name,
        source_url = source_url,
        common_name = common_name,
        brand = brand,
        status = 2
    )
