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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

from django.db import models
from django.template.defaultfilters import slugify  # django.utils.text.slugify in django 1.5!
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.core.urlresolvers import reverse
from django.core import mail

from wger.utils.constants import EMAIL_FROM


class Language(models.Model):
    '''
    Language of an item (exercise, workout, etc.)
    '''

    #e.g. 'de'
    short_name = models.CharField(max_length=2,
                                  verbose_name=_('Language short name'))

    #e.g. 'Deutsch'
    full_name = models.CharField(max_length=30,
                                 verbose_name=_('Language full name'))

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"{0} ({1})".format(self.full_name, self.short_name)


class Muscle(models.Model):
    '''
    Muscle an exercise works out
    '''

    # Name, in latin, e.g. "Pectoralis major"
    name = models.CharField(max_length=50,
                            verbose_name=_('Name'))

    # Whether to use the front or the back image for background
    is_front = models.BooleanField(default=1)

    # Metaclass to set some other properties
    class Meta:
        ordering = ["name", ]

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name

    def get_owner_object(self):
        '''
        Muscle has no owner information
        '''
        return False


class ExerciseCategory(models.Model):
    '''
    Model for an exercise category
    '''
    name = models.CharField(max_length=100,
                            verbose_name=_('Name'),)
    language = models.ForeignKey(Language,
                                 verbose_name=_('Language'),
                                 editable=False)

    # Metaclass to set some other properties
    class Meta:
        verbose_name_plural = _("Exercise Categories")
        ordering = ["name", ]

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name

    def get_owner_object(self):
        '''
        Category has no owner information
        '''
        return False


class Exercise(models.Model):
    '''
    Model for an exercise
    '''

    EXERCISE_STATUS_PENDING = '1'
    EXERCISE_STATUS_ACCEPTED = '2'
    EXERCISE_STATUS_DECLINED = '3'
    EXERCISE_STATUS_ADMIN = '4'
    EXERCISE_STATUS_SYSTEM = '5'

    EXERCISE_STATUS = (
        (EXERCISE_STATUS_PENDING, _('Pending')),
        (EXERCISE_STATUS_ACCEPTED, _('Accepted')),
        (EXERCISE_STATUS_DECLINED, _('Declined')),
        (EXERCISE_STATUS_ADMIN, _('Submitted by administrator')),
        (EXERCISE_STATUS_SYSTEM, _('System exercise')),
    )

    EXERCISE_STATUS_OK = (EXERCISE_STATUS_ACCEPTED,
                          EXERCISE_STATUS_ADMIN,
                          EXERCISE_STATUS_SYSTEM)

    # The user that submitted the exercise
    user = models.ForeignKey(User, verbose_name=_('User'), null=True, blank=True)

    # Status
    status = models.CharField(max_length=2,
                              choices=EXERCISE_STATUS,
                              default=EXERCISE_STATUS_PENDING,
                              editable=False)

    # Submission date
    creation_date = models.DateField(_('Date'), auto_now_add=True, null=True, blank=True)

    # Exercise description
    category = models.ForeignKey(ExerciseCategory,
                                 verbose_name=_('Category'))
    description = models.TextField(max_length=2000,
                                   blank=True,
                                   verbose_name=_('Description'))
    name = models.CharField(max_length=200,
                            verbose_name=_('Name'))

    muscles = models.ManyToManyField(Muscle,
                                     verbose_name=_('Primary muscles'),
                                     )

    muscles_secondary = models.ManyToManyField(Muscle,
                                               verbose_name=_('Secondary muscles'),
                                               related_name='secondary_muscles',
                                               null=True,
                                               blank=True
                                               )

    # Metaclass to set some other properties
    class Meta:
        ordering = ["name", ]

    def get_absolute_url(self):
        '''
        Returns the canonical URL to view an exercise
        '''
        return reverse('wger.exercises.views.exercises.view',
                       kwargs={'id': self.id, 'slug': slugify(self.name)})

    def get_owner_object(self):
        '''
        Exercise has no owner information
        '''
        return False

    def send_email(self, request):
        '''
        Sends an email after being sucessfully added to the database (for user
        submitted exercises only)
        '''
        if self.user and self.user.email:
            url = request.build_absolute_uri(self.get_absolute_url())
            subject = _('Exercise was sucessfully added to the general database')
            message = (ugettext("Your exercise '{0}' was successfully added to the general"
                       "database.\n\n"
                       "It is now available on the exercise and muscle overview and can be\n"
                       "added to workouts. You can access it on this address:\n"
                       "{1}\n\n").format(self.name, url) +
                       ugettext("Thank you for contributing and making this site better!\n"
                       "   the wger.de team"))
            mail.send_mail(subject,
                           message,
                           EMAIL_FROM,
                           [self.user.email],
                           fail_silently=True)

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name


class ExerciseComment(models.Model):
    '''
    Model for an exercise comment
    '''
    exercise = models.ForeignKey(Exercise,
                                 verbose_name=_('Exercise'),
                                 editable=False)
    comment = models.CharField(max_length=200,
                               verbose_name=_('Comment'),
                               help_text=_('A comment about how to correctly do this exercise.'))

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.comment

    def get_owner_object(self):
        '''
        Comment has no owner information
        '''
        return False
