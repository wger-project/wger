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

from django.utils.translation import ugettext as _

from wger.utils.widgets import BootstrapSelectMultiple


class MuscleTranslatedSelectMultiple(BootstrapSelectMultiple):
    '''
    A SelectMultiple widget that translates the options
    '''

    def render_option(self, selected_choices, option_value, option_label):

        # No translation, output only the original
        if option_label == _(option_label):
            out_string = option_label

        # There is a translation, show both
        else:
            out_string = u'{0} - {1}'.format(option_label, _(option_label))

        return super(MuscleTranslatedSelectMultiple, self).render_option(selected_choices,
                                                                         option_value,
                                                                         out_string)
