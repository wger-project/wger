"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test import LiveServerTestCase
from django.core.urlresolvers import reverse

from selenium.webdriver.common.keys import Keys

from manager.tests.testcase import WorkoutManagerLiveServerTestCase

class WeigtTest(WorkoutManagerLiveServerTestCase):

    
    def test_weight_index_empty(self):
        """
        Tests that the weight overview page has no content if there are no
        weight entries
        """
        
        self.user_login()
        self.browser.get(self.live_server_url + reverse('weight.views.overview'))
        
        # No diagram
        svg = self.browser.find_elements_by_tag_name('svg')
        self.assertFalse(svg)
        
        # Warning box
        warning_box = self.browser.find_elements_by_id('weight-box-warning')
        self.assertTrue(warning_box)

    def add_weight_entry(self, weight=80, day_index=0):
        """
        Tests that it's possible to add a weight entry and that this appears
        in the overview
        """
        
        
        
        # Clink on the link and enter the weight in the modal dialog
        add_entry_link = self.browser.find_elements_by_id('add-weight-entry')
        self.assertTrue(add_entry_link)
        
        add_entry_link[0].click()
        
        modal_dialog = self.browser.find_elements_by_class_name('ui-dialog')[0]
        self.assertTrue(modal_dialog)
        
        # Found the title
        dialog_title = modal_dialog.find_elements_by_id('ui-id-1')
        self.assertTrue(dialog_title)
        
        # Found the content
        dialog_content = modal_dialog.find_elements_by_id('ajax-info')[0]
        self.assertTrue(dialog_content)
        
        # Put some number into the weight input
        weight_input = modal_dialog.find_elements_by_id('id_weight')[0]
        self.assertTrue(weight_input)
        weight_input.send_keys(weight)
        
        # Focus on the date, a date picker should appear, select something
        date_input = modal_dialog.find_elements_by_id('id_creation_date')[0]
        self.assertTrue(date_input)
        date_input.click()
        datepicker_div = self.browser.find_elements_by_id('ui-datepicker-div')[0]
        day = datepicker_div.find_elements_by_tag_name('tbody')[0].find_elements_by_tag_name('a')[day_index]
        day.click()
        
        save_button = dialog_content.find_element_by_id('form-save')
        save_button.click()
    
    def test_add_weight_entry(self):
        """
        Tests that it's possible to add a weight entry and that this appears
        in the overview
        """
        
        self.user_login()
        self.browser.get(self.live_server_url + reverse('weight.views.overview'))
        self.add_weight_entry()
    
    def test_weight_index_data(self):
        """
        Tests that after adding weight entries, there is a diagram generated
        """
        
        self.user_login()
        self.browser.get(self.live_server_url + reverse('weight.views.overview'))
        self.add_weight_entry(70, 0)
        self.add_weight_entry(71, 1)
        self.add_weight_entry(76, 2)
        self.add_weight_entry(80, 3)
        self.add_weight_entry(86, 4)
        self.add_weight_entry(81, 5)
        self.add_weight_entry(83, 7)
        
        # There is a diagram with 8 data points
        svg_points = self.browser.find_elements_by_tag_name('circle')
        self.assertTrue(len(svg_points), 8)
        
        # There is no warning box anymore
        warning_box = self.browser.find_elements_by_id('weight-box-warning')
        self.assertFalse(warning_box)