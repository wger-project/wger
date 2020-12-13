#!/bin/sh

# -*- coding: utf-8 -*-

wget https://static.openfoodfacts.org/data/openfoodfacts-mongodbdump.tar.gz

tar xzvf openfoodfacts-mongodbdump.tar.gz
docker pull mongo
docker run -it --name wger_mongo -v $(pwd)/dump:/tmp/mongo_dump -p 27017:27017 -d mongo:latest
mongorestore -d off -c products tmp/mongo_dump/off/products.bson

python create_ingredients_from_foodfacts.py

rm openfoodfacts-mongodbdump.tar.gz