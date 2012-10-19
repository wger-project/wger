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

from django.test import TestCase

class WorkoutManagerTestCase(TestCase):
    fixtures = ['tests-user-data', 'test-exercises', ]
    
    def user_login(self, user='admin'):
        """Login the user, by default as 'admin'
        """
        self.client.login(username=user, password='%(user)s%(user)s' % {'user': user})
        
    def user_logout(self):
        """Visit the logout page
        """
        self.client.logout()
