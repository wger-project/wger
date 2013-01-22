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


"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.core.urlresolvers import reverse

from wger.manager.tests.testcase import WorkoutManagerTestCase

class DashboardTestCase(WorkoutManagerTestCase):
    """Dashboard (landing page) test case"""
  
    
    def dashboard(self, logged_in = False):
        """Helper function to test the dashboard"""
        
        response = self.client.get(reverse('manager.views.index'))
        
        if logged_in:
            # Page exists
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed('index.html')
            
            # Correct tab is selected
            self.assertEqual(response.context['active_tab'], 'user')
            
            # Check data sent to the template
            self.assertFalse(response.context['weight'])
            self.assertTrue(response.context['current_workout'])
            self.assertFalse(response.context['plan'])
            
        else:
            # Anonymous users are redirected to the login page
            self.assertEqual(response.status_code, 302)
            self.assertTemplateUsed('login.html')    
        
        
        #
        # Now, with workout
        #
        self.client.get(reverse('manager.views.add'))
        response = self.client.get(reverse('manager.views.index'))
        
        if logged_in:
            # There is something to send to the template
            self.assertFalse(response.context['weight'])
            self.assertTrue(response.context['current_workout'])
            self.assertFalse(response.context['plan'])
            
        else:
            # Anonymous users are still redirected to the login page
            self.assertEqual(response.status_code, 302)
            self.assertTemplateUsed('login.html')    
        
        
        #
        # Now, with nutrition plan
        #
        self.client.get(reverse('nutrition.views.add'))
        response = self.client.get(reverse('manager.views.index'))
        
        if logged_in:
            # There is something to send to the template
            self.assertFalse(response.context['weight'])
            self.assertTrue(response.context['current_workout'])
            self.assertTrue(response.context['plan'])
            
        else:
            # Anonymous users are still redirected to the login page
            self.assertEqual(response.status_code, 302)
            self.assertTemplateUsed('login.html')    
        
        
        #
        # Now, with weight
        #
        self.client.post(reverse('weight-add'),
                        {'weight': 100,
                         'creation_date': '2012-01-01'},
                        )
        response = self.client.get(reverse('manager.views.index'))
        
        if logged_in:
            # There is something to send to the template
            self.assertTrue(response.context['weight'])
            self.assertTrue(response.context['current_workout'])
            self.assertTrue(response.context['plan'])
            
        else:
            # Anonymous users are still redirected to the login page
            self.assertEqual(response.status_code, 302)
            self.assertTemplateUsed('login.html')    
        
        
    def test_dashboard_anonymous(self):
        '''Test index page as anonymous user'''
        
        self.user_logout()
        self.dashboard()
        
    
    def test_dashboard_logged_in(self):
        '''Test index page a logged in user'''
        
        self.user_login()
        self.dashboard(logged_in = True)
        self.user_logout()
        
