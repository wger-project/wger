# Import Open Food Facts products

This docker compose helps import or update products from the Open Food Facts
database into wger.

Note that the OFF database dump is very large, and you will need several times
this size available on your computer (tar.gz-file, extracted dump, mongo).

## 1

Download a current dump of their database

```shell
cd dump
wget https://static.openfoodfacts.org/data/openfoodfacts-mongodbdump.tar.gz
tar xzvf openfoodfacts-mongodbdump.tar.gz
```

## 2

Import the data into mongo.

Note that we are running this as a manual step since the import takes a while

```shell
docker compose up
docker compose exec mongodb mongorestore --username off --password off-wger -d admin -c products /dump/off/products.bson
```

There is also an admin interface available at <http://localhost:8081>, log in with
these credentials:

* admin
* pass

## 3

Run the import script

```shell
python manage.py import-off-products
```

To update the data fixtures:

```shell
python manage.py dumpdata nutrition > extras/scripts/data.json
cd extras/scripts
python filter-fixtures.py
zip ingredients.json.zip ingredients.json 
zip weight_units.json.zip weight_units.json
zip ingredient_units.json.zip ingredient_units.json
```

## 4

Don't forget to delete the dump and remove the containers if you love your
hard disk

```shell
docker compose down
rm dump -r openfoodfacts-mongodbdump.tar.gz dump/dump
```
