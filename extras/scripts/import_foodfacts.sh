#!/bin/sh

# -*- coding: utf-8 -*-

wget https://static.openfoodfacts.org/data/openfoodfacts-mongodbdump.tar.gz

tar xzvf openfoodfacts-mongodbdump.tar.gz
docker pull mongo
run --name wger_mongo --mount type=bind,source='"C:\Users\User\GitHub\openfoodfacts\dump"',target=/tmp/mongo_dump -p 27017:27017 -d mongo

python create_ingredients_from_foodfacts.py

rm openfoodfacts-mongodbdump.tar.gz