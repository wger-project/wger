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

import logging
from django.http import HttpResponseNotFound

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from wger.manager.routines.korte import korte

logger = logging.getLogger('wger.custom')

routines = {'korte': korte}


def overview(request):
    '''
    An overview of all the available routines
    '''
    context = {'routines': routines}
    return render(request, 'routines/overview.html', context)


def detail(request, name):
    '''
    Detail view for a routine
    '''

    context = {}
    try:
        context['routine'] = routines[name]
    except KeyError:
        return HttpResponseNotFound()

    return render(request, 'routines/detail.html', context)
