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

# Standard Library
import logging

# Third Party
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

# wger
from wger.core.models import (
    Language,
    UserProfile
)
from wger.gym.helpers import is_any_gym_admin
from wger.gym.models import (
    Gym,
    GymUserConfig
)
from wger.utils.cache import (
    cache_mapper,
    delete_template_fragment_cache
)


logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class LanguageConfig(models.Model):
    '''
    Configuration for languages

    Allows to specify what exercises and ingredients are shown for each language
    '''
    SHOW_ITEM_EXERCISES = '1'
    SHOW_ITEM_INGREDIENTS = '2'
    SHOW_ITEM_LIST = (
        (SHOW_ITEM_EXERCISES, _('Exercises')),
        (SHOW_ITEM_INGREDIENTS, _('Ingredients')),
    )

    language = models.ForeignKey(Language,
                                 related_name='language_source',
                                 editable=False)
    language_target = models.ForeignKey(Language,
                                        related_name='language_target',
                                        editable=False)
    item = models.CharField(max_length=2,
                            choices=SHOW_ITEM_LIST,
                            editable=False)
    show = models.BooleanField(default=1)

    class Meta:
        '''
        Set some other properties
        '''
        ordering = ["item", "language_target", ]

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return u"Config for language {0}".format(self.language)

    def save(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''

        super(LanguageConfig, self).save(*args, **kwargs)

        # Cached objects
        cache.delete(cache_mapper.get_language_config_key(self.language, self.item))

        # Cached template fragments
        delete_template_fragment_cache('muscle-overview', self.language_id)
        delete_template_fragment_cache('exercise-overview', self.language_id)

    def delete(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''

        # Cached objects
        cache.delete(cache_mapper.get_language_config_key(self.language, self.item))

        # Cached template fragments
        delete_template_fragment_cache('muscle-overview', self.language_id)
        delete_template_fragment_cache('exercise-overview', self.language_id)

        super(LanguageConfig, self).delete(*args, **kwargs)


@python_2_unicode_compatible
class GymConfig(models.Model):
    '''
    System wide configuration for gyms

    At the moment this only allows to set one gym as the default
    TODO: close registration (users can only become members thorough an admin)
    '''

    default_gym = models.ForeignKey(Gym,
                                    verbose_name=_('Default gym'),
                                    help_text=_('Select the default gym for this installation. '
                                                'This will assign all new registered users to this '
                                                'gym and update all existing users without a '
                                                'gym.'),
                                    null=True,
                                    blank=True)
    '''
    Default gym for the wger installation
    '''

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return u"Default gym {0}".format(self.default_gym)

    def save(self, *args, **kwargs):
        '''
        Perform additional tasks
        '''
        if self.default_gym:

            # All users that have no gym set in the profile are edited
            UserProfile.objects.filter(gym=None).update(gym=self.default_gym)

            # All users in the gym must have a gym config
            for profile in UserProfile.objects.filter(gym=self.default_gym):
                user = profile.user
                if not is_any_gym_admin(user):
                    try:
                        user.gymuserconfig
                    except GymUserConfig.DoesNotExist:
                        config = GymUserConfig()
                        config.gym = self.default_gym
                        config.user = user
                        config.save()
                        logger.debug('Creating GymUserConfig for user {0}'.format(user.username))

        return super(GymConfig, self).save(*args, **kwargs)


@python_2_unicode_compatible
class UserCanCreate(models.Model):
    user = models.OneToOneField(User,
                                editable=False)
    '''
    The user
    '''
    DENY = 'DENY'
    REVIEW = 'REVIEW'
    ACCEPT = 'ACCEPT'
    USER_PERMISSION_CHOICES = (
        (DENY, 'DENY - user cannot create new items'),
        (REVIEW, 'REVIEW - user may submit item for approval'),
        (ACCEPT, 'ACCEPT - user can create items without approval'),
    )

    ingredient_perm = models.CharField(max_length=6,
                                       verbose_name=_('Allow user to submit new ingredient'),
                                       help_text=_('Allow user to submit new ingredient'),
                                       choices=USER_PERMISSION_CHOICES,
                                       default=REVIEW,
                                       )

    exercise_perm = models.CharField(max_length=6,
                                     verbose_name=_('Allow user to submit new exercise'),
                                     help_text=_('Allow user to submit new exercise'),
                                     choices=USER_PERMISSION_CHOICES,
                                     default=REVIEW,
                                     )

    def ingredient_create_perm(self):
        if is_any_gym_admin(self.user):
            return True
        elif self.ingredient_perm == 'REVIEW' or self.ingredient_perm == 'ACCEPT':
            return True
        else:
            return False

    def ingredient_needs_review(self):
        if self.ingredient_perm == 'ACCEPT':
            return False
        else:
            return True

    def create_exercise(self):
        if is_any_gym_admin(self.user):
            return True
        elif self.exercise_perm == 'REVIEW' or self.exercise_perm == 'ACCEPT':
            return True
        else:
            return False

    def exercise_needs_review(self):
        if self.exercise_perm == 'ACCEPT':
            return False
        else:
            return True
