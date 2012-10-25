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

from django.core.urlresolvers import reverse

from django.test import TestCase
from django.test import LiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

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


class WorkoutManagerLiveServerTestCase(LiveServerTestCase):
    """
    Live server test case, will be used with the selenium webdriver
    """
    
    fixtures = ['tests-user-data', 'test-exercises', ]
    

    def setUp(self):
        """
        Set up out testing browser
        """
        
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
        
        
    def tearDown(self):
        """
        Quit the browser
        """
        
        self.browser.quit()
        
    
    def user_login(self, user='admin'):
        """
        Login the user
        """
        
        self.browser.get(self.live_server_url + reverse('manager.views.login'))
        username_field = self.browser.find_element_by_id('id_username')
        username_field.send_keys('admin')
        
        password_field = self.browser.find_element_by_id('id_password')
        password_field.send_keys('%(user)s%(user)s' % {'user': user})
        password_field.send_keys(Keys.RETURN)
        
    def user_logout(self, user='admin'):
        """
        Logout the user
        """
        
        self.browser.get(self.live_server_url + reverse('manager.views.logout'))
    