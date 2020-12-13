from pymongo import MongoClient
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
import django
django.setup()
from wger.nutrition.models import Ingredient

client = MongoClient(port=27017)
db = client.off

# loop through each product and create Ingredient object
# INGREDIENT = language, creation_date (auto to now), update_date (auto to now), name, 
    # energy, protein, fiber, carbs, sugar, fat, saturated, sodium, code, source_name, source_url, 
    # last_imported, common_name, image, category, brand 

# print(db.getCollectionNames())
for product in db.products.find({"lang": "de"}):
    name = product['product_name']
    lang = product['lang']
    # nutriment data not always complete (should make these all optional)
    energy = product['nutriments']['energy-kcal_100g']
    protein = product['nutriments']['proteins_100g']
    fiber = product['nutriments']['fiber_100g']
    carbs = product['nutriments']['carbohydrates_100g']
    sugar = product['nutriments']['sugars_100g']
    fat = product['nutriments']['fat_100g']
    saturated = product['nutriments']['saturated-fat_100g']
    sodium = product['nutriments']['sodium_100g']
    
    code = product['code']
    # source_name = 
    # source_url = 
    # last_imported = default today?
    common_name = product['generic_name'] # often empty
    # image = 
    # category = 
    brand = product['brands']
    print(name)
    break   
# english, german, bulgarian, greek, spanish, russian, dutch, portuguese, czech, swedish, norwegian, french

# Ingredient.create(blah)
