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
import logging

from django.core.urlresolvers import reverse

from manager.tests.testcase import WorkoutManagerLiveServerTestCase

logger = logging.getLogger('workout_manager.custom')


class NutritionTest(WorkoutManagerLiveServerTestCase):

    def test_create_plan(self):
        """
        Tests that it's possible to create a complete nutritional plan
        """

        self.browser.get(self.live_server_url + reverse('nutrition.views.overview'))
        self.user_login(explicit_login=False)

        # No plans, there is a warning box
        box = self.browser.find_elements_by_id('nutrition-box-warning')
        self.assertTrue(box)

        # Clink on the link and enter the weight in the modal dialog
        create_link = self.browser.find_elements_by_id('nutrition-create-new')
        self.assertTrue(create_link)
        create_link[0].click()

        # No meals, there is a warning box
        box = self.browser.find_elements_by_id('meal-box-warning')[0]
        self.assertTrue(box)

        # Clink on the link and enter the time in the modal dialog
        create_link = box.find_elements_by_tag_name('a')
        self.assertTrue(create_link)
        create_link[0].click()

        # Check that there is a modal dialog
        (dialog_title, dialog_content) = self.check_modal_dialog()

        # Put some number into the time field
        weight_input = dialog_content.find_elements_by_id('id_time')[0]
        self.assertTrue(weight_input)
        weight_input.send_keys('8:00')

        save_button = dialog_content.find_element_by_id('form-save')
        save_button.click()

        # Warning box for meals has disappeared
        box = self.browser.find_elements_by_id('meal-box-warning')
        self.assertFalse(box)

        # There is now 1 warning box for ingredients
        box = self.browser.find_elements_by_class_name('ingredient-box-warning')
        self.assertEqual(len(box), 1)

        # Click on the link to add a new ingredient
        create_link = box[0].find_elements_by_tag_name('a')[0]
        self.assertTrue(create_link)
        create_link.click()

        # Check that there is a modal dialog
        (dialog_title, dialog_content) = self.check_modal_dialog()

        # Set the data
        #id_amount_gramm
        amount_input = dialog_content.find_elements_by_id('id_amount_gramm')[0]
        self.assertTrue(amount_input)
        amount_input.send_keys('150')

        ingredient_autocomplete = dialog_content.find_elements_by_id('id_ingredient_searchfield')[0]
        self.assertTrue(ingredient_autocomplete)

        #We want to find "Ingredient, test, 2, organic, raw"
        ingredient_autocomplete.click()
        ingredient_autocomplete.send_keys('raw')
        autocompleter_input = self.browser.find_elements_by_class_name('ui-autocomplete')[0]
        self.assertTrue(amount_input, 'Ingredient autocompleter not found')
        # there is one result
        autocompleter_result = self.browser.find_elements_by_class_name('ui-menu-item')
        self.assertEqual(len(autocompleter_result), 1)
        autocompleter_result[0].click()

        save_button = dialog_content.find_element_by_id('form-save')
        save_button.click()

        # Warning box for ingredients has disappeared
        box = self.browser.find_elements_by_class_name('ingredient-box-warning')
        self.assertFalse(box)


