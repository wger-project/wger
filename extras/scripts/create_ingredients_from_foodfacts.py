from pymongo import MongoClient
from wger.nutrition.models import Ingredient

client = MongoClient('192.168.178.20', 27017)
db = client.off

# loop through each product and create Ingredient object
# INGREDIENT = language, creation_date (auto to now), update_date (auto to now), name, 
    # energy, protein, fiber, carbs, sugar, fat, saturated, sodium, code, source_name, source_url, 
    # last_imported, common_name, image, category, brand 


for product in db.find({"lang": "de"}):
    name = product.get('product_name')
    print(name)   
# english, german, bulgarian, greek, spanish, russian, dutch, portuguese, czech, swedish, norwegian, french

# Ingredient.create(blah)