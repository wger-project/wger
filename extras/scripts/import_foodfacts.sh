#!/bin/sh

# -*- coding: utf-8 -*-

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

"""
Simple script that imports and loads the Open Food Facts database into the 
ingredients database

NOTE: The file is VERY large (17 GB), so it takes a long time (> 3 hours) to run
and create all ingredients
"""

wget https://static.openfoodfacts.org/data/openfoodfacts-mongodbdump.tar.gz

tar xzvf openfoodfacts-mongodbdump.tar.gz
docker pull mongo
docker run -it --name wger_mongo -v $(pwd)/dump:/tmp/mongo_dump -p 27017:27017 -d mongo:latest
mongorestore -d off -c products tmp/mongo_dump/off/products.bson

python create_ingredients_from_foodfacts.py

rm $(pwd)/openfoodfacts-mongodbdump.tar.gz
rm -r $(pwd)/dump
rm -r /tmp