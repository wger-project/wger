# -*- coding: iso-8859-15 -*-
'''
Simple FunkLoad test
'''
import unittest
from random import random
from funkload.FunkLoadTestCase import FunkLoadTestCase

class Simple(FunkLoadTestCase):
    '''
    This test uses the configuration file Simple.conf.
    '''

    def setUp(self):
        '''
        Setting up test.
        '''
        self.server_url = self.conf_get('main', 'url')

    def test_simple(self):
        # The description should be set in the configuration file
        server_url = self.server_url

        # Exercises        
        self.get(server_url + '/en/exercise/overview/', description='Get exercise overview')
        self.get(server_url + '/en/exercise/muscle/overview/', description='Get muscle overview')
        self.get(server_url + '/de/exercise/79/view/', description='Get exercise page')

        # Nutrition
        self.get(server_url + '/de/nutrition/ingredient/overview/', description='Get ingredient overview')
        self.get(server_url + '/de/nutrition/ingredient/8304/view/4-korn-waffeln/', description='Get ingredient page')


if __name__ in ('main', '__main__'):
    unittest.main()
