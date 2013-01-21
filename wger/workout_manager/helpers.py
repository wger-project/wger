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

import decimal
import json

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def pagination(object_list,
               request_page,
               paginator_class = Paginator,
               objects_per_page = 25,
               max_total_pages = 10,
               pages_around_current = 5):
    """
    Helper function to initialise the pagination.
    
    If the list is too long, only pages around the current one are shown.
    """
    
    paginator = paginator_class(object_list, objects_per_page)
    
    try:
        paginated_page = paginator.page(request_page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        paginated_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_page = paginator.page(paginator.num_pages)
    
    
    # For very long lists (e.g. the English ingredient with more than 8000 items)
    # we muck around here to remove the pages not inmediately 'around' the current
    # one, otherwise we end up with a which a useless block with 300 pages.
    if paginator.num_pages > max_total_pages:
        
        start_page = paginated_page.number - pages_around_current
        for i in range(paginated_page.number - pages_around_current, paginated_page.number +1):
            if i > 0:
                start_page = i
                break
        
        end_page = paginated_page.number + pages_around_current
        for i in range(paginated_page.number, paginated_page.number + pages_around_current):
            if i > paginator.num_pages:
                end_page = i
                
                break
        
        page_range = range(start_page, end_page)
    else:
        page_range = paginator.page_range
    
    # OK, return
    return({'page': paginated_page,
            'page_range': page_range})
            

class DecimalJsonEncoder(json.JSONEncoder):
    '''
    Custom JSON encoder.
    
    This class is needed because we store some data as a decimal (e.g. the
    individual weight entries in the workout log) and they need to be
    processed, json.dumps() doesn't work on them
    '''
    def _iterencode(self, o, markers=None):
        if isinstance(o, decimal.Decimal):
            return (str(o) for o in [o])
            
        return super(DecimalJsonEncoder, self)._iterencode(o, markers)
