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
docker compose exec mongorestore --username off --password off-wger -d admin -c products /dump/off/products.bson
```

There is an admin interface available at <http://localhost:80801>, log in with
these credentials:

* admin
* pass

## 3

Run the import script

```shell
python manage.py import-off-products
```

## 4

Don't forget to delete the dump and remove the containers if you love your
hard disk

```shell
docker compose down
rm dump -r openfoodfacts-mongodbdump.tar.gz dump/off
```
