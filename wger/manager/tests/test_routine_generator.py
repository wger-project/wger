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

from django.core.urlresolvers import reverse

from wger.manager import routines
from wger.manager.tests.testcase import WorkoutManagerTestCase


class RoutineOverviewAccessTestCase(WorkoutManagerTestCase):
    '''
    Test accessing the routine overview page
    '''

    def routine_overview(self):
        '''
        Helper function to test accessing the routine overview
        '''
        response = self.client.get(reverse('manager:routine:generator'))
        self.assertEqual(response.status_code, 200)

    def test_routine_overview_anonymous(self):
        '''
        Tests accessing the routine overview page as an anonymous user
        '''
        self.routine_overview()

    def test_routine_overview_logged_in(self):
        '''
        Tests accessing the routine overview page as a logged in user
        '''
        self.user_login('test')
        self.routine_overview()


class RoutinePdfExportTestCase(WorkoutManagerTestCase):
    '''
    Tests exporting the routines as a pdf
    '''

    def export_pdf(self):
        '''
        Helper function to test exporting a routine as a pdf
        '''

        # To modify the session and then save it, it must be stored in a variable
        # first (because a new SessionStore is created every time this property
        # is accessed)
        session = self.client.session
        session['routine_config'] = {'round_to': 2.5,
                                     'max_squat': 120,
                                     'max_bench': 130,
                                     'max_deadlift': 150}
        session.save()

        # Create a PDF for all available routines
        for routine in routines.get_routines():

            response = self.client.get(reverse('manager:routine:pdf', kwargs={'name': routine}))

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'application/pdf')
            self.assertEqual(response['Content-Disposition'],
                             'attachment; filename=Routine-{0}.pdf'.format(routine))

            # Approximate size only
            self.assertGreater(int(response['Content-Length']), 44000)
            self.assertLess(int(response['Content-Length']), 53000)

    def test_export_pdf_anonymous(self):
        '''
        Tests exporting a routine as a pdf as an anonymous user
        '''

        # TODO: it seems it's not possible to use the session for anonymous users
        #       https://code.djangoproject.com/ticket/10899
        # self.export_pdf()

    def test_export_pdf_logged_in(self):
        '''
        Tests exporting a routine as a pdf as a logged in user
        '''

        self.user_login('test')
        self.export_pdf()
