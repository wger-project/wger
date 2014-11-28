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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.


def reps_smart_text(settings, set_obj):
    '''
    "Smart" textual representation
    This is a human representation of the settings, in a way that humans
    would also write: e.g. "8 8 10 10" but "4 x 10" and not "10 10 10 10"

    :param settings:
    :param set_obj:
    :return setting_text, setting_list:
    '''
    if len(settings) == 0:
        setting_text = ''
        setting_list = []
    elif len(settings) == 1:
        reps = settings[0].reps if settings[0].reps != 99 else u'∞'
        setting_text = u'{0} × {1}'.format(set_obj.sets, reps)
        setting_list = [settings[0].reps] * set_obj.sets
    elif len(settings) > 1:
        tmp_reps_text = []
        tmp_reps = []
        for i in settings:
            reps = str(i.reps) if i.reps != 99 else u'∞'
            tmp_reps_text.append(reps)
            tmp_reps.append(i.reps)

        setting_text = u' – '.join(tmp_reps_text)
        setting_list = tmp_reps

    return setting_text, setting_list
