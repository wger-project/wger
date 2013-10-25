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

import logging

from django.db import models
from django.template.defaultfilters import slugify  # django.utils.text.slugify in django 1.5!
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext
from django.core.urlresolvers import reverse
from django.core import mail
from django.core.cache import cache
from django.db.models.signals import pre_save
from django.db.models.signals import pre_delete
from django.db.models.signals import post_delete

from easy_thumbnails.files import get_thumbnailer

from wger.utils.constants import EMAIL_FROM
from wger.utils.cache import delete_template_fragment_cache
from wger.utils.cache import cache_mapper


logger = logging.getLogger('wger.custom')


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

    #
    # Django methods
    #
    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"{0} ({1})".format(self.full_name, self.short_name)

    def get_absolute_url(self):
        '''
        Returns the canonical URL to view a language
        '''
        return reverse('config:language-view', kwargs={'pk': self.id})

    #
    # Own methods
    #
    def get_owner_object(self):
        '''
        Muscle has no owner information
        '''
        return False


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

    category = models.ForeignKey(ExerciseCategory,
                                 verbose_name=_('Category'))
    description = models.TextField(max_length=2000,
                                   verbose_name=_('Description'))
    '''Description on how to perform the exercise'''

    name = models.CharField(max_length=200,
                            verbose_name=_('Name'))

    muscles = models.ManyToManyField(Muscle,
                                     verbose_name=_('Primary muscles'),
                                     )
    '''Main muscles trained by the exercise'''

    muscles_secondary = models.ManyToManyField(Muscle,
                                               verbose_name=_('Secondary muscles'),
                                               related_name='secondary_muscles',
                                               null=True,
                                               blank=True
                                               )
    '''Secondary muscles trained by the exercise'''

    # Non-editable fields
    user = models.ForeignKey(User, verbose_name=_('User'), null=True, blank=True)
    '''The user that submitted the exercise'''

    status = models.CharField(max_length=2,
                              choices=EXERCISE_STATUS,
                              default=EXERCISE_STATUS_PENDING,
                              editable=False)
    '''Status, e.g. accepted or declined'''

    creation_date = models.DateField(_('Date'), auto_now_add=True, null=True, blank=True)
    '''The submission date'''

    language = models.ForeignKey(Language,
                                 verbose_name=_('Language'),
                                 editable=False)
    '''The exercise's language'''

    #
    # Django methods
    #

    # Metaclass to set some other properties
    class Meta:
        ordering = ["name", ]

    def get_absolute_url(self):
        '''
        Returns the canonical URL to view an exercise
        '''
        return reverse('wger.exercises.views.exercises.view',
                       kwargs={'id': self.id, 'slug': slugify(self.name)})

    def save(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''

        super(Exercise, self).save(*args, **kwargs)

        # Cached objects
        cache.delete(cache_mapper.get_exercise_key(self))
        cache.delete(cache_mapper.get_exercise_muscle_bg_key(self))

        # Cached template fragments
        delete_template_fragment_cache('muscle-overview', self.language_id)
        delete_template_fragment_cache('exercise-overview', self.language_id)
        delete_template_fragment_cache('exercise-detail-header', self.id, self.language_id)
        delete_template_fragment_cache('exercise-detail-muscles', self.id, self.language_id)

    def delete(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''

        # Cached objects
        cache.delete(cache_mapper.get_exercise_key(self))
        cache.delete(cache_mapper.get_exercise_muscle_bg_key(self))

        # Cached template fragments
        delete_template_fragment_cache('muscle-overview', self.language_id)
        delete_template_fragment_cache('exercise-overview', self.language_id)
        delete_template_fragment_cache('exercise-detail-header', self.language_id)
        delete_template_fragment_cache('exercise-detail-muscles', self.language_id)

        super(Exercise, self).delete(*args, **kwargs)

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name

    #
    # Own methods
    #

    @property
    def main_image(self):
        '''
        Return the main image for the exercise or None if nothing is found
        '''
        has_image = self.exerciseimage_set.exists()
        image = None
        if has_image:
            image = self.exerciseimage_set.filter(is_main=True)[0]
        return image

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


def exercise_image_upload_dir(instance, filename):
    '''
    Returns the upload target for exercise images
    '''
    return "exercise-images/{0}/{1}".format(instance.exercise.id, filename)


class ExerciseImage(models.Model):
    '''
    Model for an exercise image
    '''
    exercise = models.ForeignKey(Exercise,
                                 verbose_name=_('Exercise'),
                                 editable=False)
    '''The exercise the image belongs to'''

    image = models.ImageField(verbose_name=_('Image'),
                              help_text=_('Only PNG and JPEG formats are supported'),
                              upload_to=exercise_image_upload_dir)
    '''Uploaded image'''

    is_main = models.BooleanField(verbose_name=_('Is main picture'),
                                  default=False,
                                  help_text=_("Tick the box if you want set this image as the main "
                                              "one for the exercise (will be shown e.g. in the "
                                              "search)"))
    '''A flag indicating whether the schedule should act as a loop'''

    class Meta:
        '''
        Set default ordering
        '''
        ordering = ['-is_main', ]

    def get_owner_object(self):
        '''
        Image has no owner information
        '''
        return False

    def save(self, *args, **kwargs):
        '''
        Only one image can be marked as main picture at a time
        '''
        if self.is_main:
            ExerciseImage.objects.filter(exercise=self.exercise).update(is_main=False)
            self.is_main = True

        # If the exercise has only one image, mark it as main
        if not ExerciseImage.objects.filter(exercise=self.exercise, is_main=False).count():
            self.is_main = True

        #
        # Reset all cached infos
        #
        delete_template_fragment_cache('muscle-overview', self.exercise.language_id)
        delete_template_fragment_cache('exercise-overview', self.exercise.language_id)
        delete_template_fragment_cache('exercise-detail-header',
                                       self.exercise.id,
                                       self.exercise.language_id)
        delete_template_fragment_cache('exercise-detail-muscles',
                                       self.exercise.id,
                                       self.exercise.language_id)

        # And go on
        super(ExerciseImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''
        super(ExerciseImage, self).delete(*args, **kwargs)

        delete_template_fragment_cache('muscle-overview', self.exercise.language_id)
        delete_template_fragment_cache('exercise-overview', self.exercise.language_id)
        delete_template_fragment_cache('exercise-detail-header', self.exercise.language_id)
        delete_template_fragment_cache('exercise-detail-muscles', self.exercise.language_id)

        # Make sure there is always a main image
        if not ExerciseImage.objects.filter(exercise=self.exercise, is_main=True).count():
            image = ExerciseImage.objects.filter(exercise=self.exercise).filter(is_main=False)[0]
            image.is_main = True
            image.save()


def delete_exercise_image_on_delete(sender, instance, **kwargs):
    '''
    Delete the image, along with its thumbnails, from the disk
    '''

    thumbnailer = get_thumbnailer(instance.image)
    thumbnailer.delete_thumbnails()
    instance.image.delete(save=False)


post_delete.connect(delete_exercise_image_on_delete, sender=ExerciseImage)


def delete_exercise_image_on_update(sender, instance, **kwargs):
    '''
    Delete the corresponding image from the filesystem when the an ExerciseImage
    object was changed
    '''
    if not instance.pk:
        return False

    try:
        old_file = ExerciseImage.objects.get(pk=instance.pk).image
    except ExerciseImage.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        thumbnailer = get_thumbnailer(instance.image)
        thumbnailer.delete_thumbnails()
        instance.image.delete(save=False)


pre_save.connect(delete_exercise_image_on_update, sender=ExerciseImage)


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
