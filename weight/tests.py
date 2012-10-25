"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class WeigtTest(LiveServerTestCase):
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
        #pass
    
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
        
        
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.browser.get(self.live_server_url)
        username_field = self.browser.find_element_by_id('id_username')
        username_field.send_keys('admin')
        
        password_field = self.browser.find_element_by_id('id_password')
        password_field.send_keys('adminadmin')
        password_field.send_keys(Keys.RETURN)
        
        self.browser.get(self.live_server_url + '/weight/overview/')
        svg = self.browser.find_elements_by_tag_name('svg')
        self.assertEqual(len(svg), 0)
