#!/bin/sh

# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License



#
# Note: you need to have the OpenSans fonts installed where inkscape can find them
#

for resolution in 16 30 32 48 60 64 114 128 256
do
    # Regular Icon
    inkscape \
    --export-png=logo-${resolution}.png \
    --export-area-page \
    --export-width ${resolution}\
    --export-height ${resolution}\
    logo.svg

    # Icon for Firefox OS
    inkscape \
    --export-png=logo-marketplace-${resolution}.png \
    --export-area-page \
    --export-width ${resolution}\
    --export-height ${resolution}\
    logo-marketplace.svg
done
