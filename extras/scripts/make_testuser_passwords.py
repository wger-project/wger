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

'''
Simple script that creates passwords for the users used in the test
'''

import json

from django.contrib.auth.hashers import make_password

out = []
out_profile = []

for i in range(1, 12):

    pk = 13 + i
    gym = 1
    if pk in (19, 20):
        gym = 2
    elif gym in (21, 22, 23, 24):
        gym = 3
    else:
        gym = 1
    
    username = 'member{}'.format(i)
    password = make_password('{0}{0}'.format(username))
    #print "User: {}\tpassword: {}".format(username, password)
    out.append({
        "pk": pk,
        "model": "auth.user",
        "fields": {
            "username": "member{}".format(i),
            "first_name": "",
            "last_name": "",
            "is_active": True,
            "is_superuser": False,
            "is_staff": False,
            "last_login": "2013-03-30T00:23:21.592Z",
            "groups": [],
            "user_permissions": [],
            "password": "{}".format(password),
            "email": "{}@example.com".format(username),
            "date_joined": "2013-03-30T00:23:21.592Z"
        }
    })
    
    out_profile.append({
        "pk": pk, 
        "model": "core.userprofile",
        "fields": {
            "is_temporary": False, 
            "show_comments": False, 
            "show_english_ingredients": False, 
            "user": pk,
            "gender": "1",
            "age": 30,
            "sport_intensity": "3",
            "calories": 3500,
            "height": 180,
            "sport_hours": 6,
            "sleep_hours": 7,
            "work_intensity": "1",
            "freetime_intensity": "1",
            "work_hours": 8,
            "freetime_hours": 8,
            "workout_reminder_active": False,
            "workout_reminder": 20,
            "workout_duration": 8,
            "notification_language": 1,
	        "timer_active": True,
	        "timer_pause": 90,
	        "gym": gym 
        }
    })


with open('tmp.txt', 'w') as the_file:
    the_file.write(json.dumps(out, indent=4))

