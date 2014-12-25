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

import six
import logging

from django.db import models
from django.template.loader import render_to_string
from django.template.defaultfilters import slugify  # django.utils.text.slugify in django 1.5!
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from django.core.urlresolvers import reverse
from django.core import mail
from django.core.cache import cache
from django.core.validators import MinLengthValidator
from django.db.models.signals import pre_save
from django.db.models.signals import post_delete
from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.signals import saved_file
from easy_thumbnails.signal_handlers import generate_aliases

from wger.core.models import Language
from wger.utils.managers import SubmissionManager
from wger.utils.models import AbstractLicenseModel
from wger.utils.models import AbstractSubmissionModel
from wger.utils.constants import EMAIL_FROM
from wger.utils.cache import delete_template_fragment_cache
from wger.utils.cache import reset_workout_canonical_form
from wger.utils.cache import cache_mapper


logger = logging.getLogger('wger.custom')


class ExerciseLanguageMapper(models.Model):
    '''
    A simple mapper used to identify the same exercises across languages

    This is only used at the moment in places like the routine generator,
    where it's necessary to know what IDs an exercise has in the different
    languages
    '''

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.get_language('en').name

    def get_language(self, language):
        '''
        Gets the exercise corresponding to the language

        Raises a KeyError if the language is not found

        :param language: the short name
        :return the exercise object
        '''
        for exercise in self.exercise_set.all():
            if exercise.language.short_name == language:
                return exercise

        raise KeyError('Language {0} not found'.format(language))

    def get_all_languages(self):
        '''
        Returns a dictionary with all available languages
        '''
        out = cache.get(cache_mapper.get_exercise_language_mapper(self))
        if not out:
            out = {}
            for exercise in self.exercise_set.all():
                out[exercise.language.short_name] = exercise
            cache.set(cache_mapper.get_exercise_language_mapper(self), out)

        return out


class Muscle(models.Model):
    '''
    Muscle an exercise works out
    '''

    name = models.CharField(max_length=50,
                            verbose_name=_('Name'),
                            help_text=_('In latin, e.g. "Pectoralis major"'))

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


class Equipment(models.Model):
    '''
    Equipment used or needed by an exercise
    '''

    name = models.CharField(max_length=50,
                            verbose_name=_('Name'))

    class Meta:
        '''
        Set default ordering
        '''
        ordering = ["name", ]

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name

    def get_owner_object(self):
        '''
        Equipment has no owner information
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

    def save(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''

        super(ExerciseCategory, self).save(*args, **kwargs)

        # Cached template fragments
        for language in Language.objects.all():
            delete_template_fragment_cache('exercise-overview', language.id)
            delete_template_fragment_cache('exercise-overview-mobile', language.id)

    def delete(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''
        for language in Language.objects.all():
            delete_template_fragment_cache('exercise-overview', language.id)
            delete_template_fragment_cache('exercise-overview-mobile', language.id)

        super(ExerciseCategory, self).delete(*args, **kwargs)


class Exercise(AbstractSubmissionModel, AbstractLicenseModel, models.Model):
    '''
    Model for an exercise
    '''

    objects = SubmissionManager()
    '''Custom manager'''

    category = models.ForeignKey(ExerciseCategory,
                                 verbose_name=_('Category'))
    description = models.TextField(max_length=2000,
                                   verbose_name=_('Description'),
                                   validators=[MinLengthValidator(40)])
    '''Description on how to perform the exercise'''

    name = models.CharField(max_length=200,
                            verbose_name=_('Name'))

    muscles = models.ManyToManyField(Muscle,
                                     verbose_name=_('Primary muscles'),
                                     null=True,
                                     blank=True)
    '''Main muscles trained by the exercise'''

    muscles_secondary = models.ManyToManyField(Muscle,
                                               verbose_name=_('Secondary muscles'),
                                               related_name='secondary_muscles',
                                               null=True,
                                               blank=True)
    '''Secondary muscles trained by the exercise'''

    equipment = models.ManyToManyField(Equipment,
                                       verbose_name=_('Equipment'),
                                       null=True,
                                       blank=True)
    '''Equipment needed by this exercise'''

    creation_date = models.DateField(_('Date'),
                                     auto_now_add=True,
                                     null=True,
                                     blank=True)
    '''The submission date'''

    language = models.ForeignKey(Language,
                                 verbose_name=_('Language'))
    '''The exercise's language'''

    language_mapper = models.ForeignKey(ExerciseLanguageMapper,
                                        null=True,
                                        blank=True,
                                        editable=False)
    '''A language mapper'''

    #
    # Django methods
    #
    class Meta:
        ordering = ["name", ]

    def get_absolute_url(self):
        '''
        Returns the canonical URL to view an exercise
        '''
        return reverse('exercise:exercise:view', kwargs={'id': self.id, 'slug': slugify(self.name)})

    def save(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''

        super(Exercise, self).save(*args, **kwargs)

        # Cached objects
        cache.delete(cache_mapper.get_exercise_key(self))
        cache.delete(cache_mapper.get_exercise_muscle_bg_key(self))

        # Cached template fragments
        for language in Language.objects.all():
            delete_template_fragment_cache('muscle-overview', language.id)
            delete_template_fragment_cache('exercise-overview', language.id)
            delete_template_fragment_cache('exercise-overview-mobile', language.id)
            delete_template_fragment_cache('exercise-detail-header', self.id, language.id)
            delete_template_fragment_cache('exercise-detail-muscles', self.id, language.id)
            delete_template_fragment_cache('equipment-overview', language.id)

        # Cached workouts
        for set in self.set_set.all():
            reset_workout_canonical_form(set.exerciseday.training_id)

    def delete(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''

        # Cached objects
        cache.delete(cache_mapper.get_exercise_key(self))
        cache.delete(cache_mapper.get_exercise_muscle_bg_key(self))

        # Cached template fragments
        for language in Language.objects.all():
            delete_template_fragment_cache('muscle-overview', language.id)
            delete_template_fragment_cache('exercise-overview', language.id)
            delete_template_fragment_cache('exercise-overview-mobile', language.id)
            delete_template_fragment_cache('exercise-detail-header', self.id, language.id)
            delete_template_fragment_cache('exercise-detail-muscles', self.id, language.id)
            delete_template_fragment_cache('equipment-overview', language.id)

        # Cached workouts
        for set in self.set_set.all():
            reset_workout_canonical_form(set.exerciseday.training.pk)

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
        return self.exerciseimage_set.accepted().filter(is_main=True).first()

    def get_owner_object(self):
        '''
        Exercise has no owner information
        '''
        return False

    def send_email(self, request):
        '''
        Sends an email after being successfully added to the database (for user
        submitted exercises only)
        '''
        try:
            user = User.objects.get(username=self.license_author)
        except User.DoesNotExist:
            return
        if self.license_author and user.email:
            translation.activate(user.userprofile.notification_language.short_name)
            url = request.build_absolute_uri(self.get_absolute_url())
            subject = _('Exercise was successfully added to the general database')
            context = {
                'exercise': self.name,
                'url': url
            }
            message = render_to_string('exercise/email_new.html', context)
            mail.send_mail(subject,
                           message,
                           EMAIL_FROM,
                           [user.email],
                           fail_silently=True)

    def set_author(self, request):
        '''
        Set author and status

        This is only used when creating exercises (via web or API)
        '''
        if request.user.has_perm('exercises.add_exercise'):
            self.status = self.STATUS_ACCEPTED
            if not self.license_author:
                self.license_author = 'wger.de'

        else:
            if not self.license_author:
                self.license_author = request.user.username

            subject = _('New user submitted exercise')
            message = _(u'The user {0} submitted a new exercise "{1}".').format(
                request.user.username, self.name)
            mail.mail_admins(six.text_type(subject),
                             six.text_type(message),
                             fail_silently=True)


def exercise_image_upload_dir(instance, filename):
    '''
    Returns the upload target for exercise images
    '''
    return "exercise-images/{0}/{1}".format(instance.exercise.id, filename)


class ExerciseImage(AbstractSubmissionModel, AbstractLicenseModel, models.Model):
    '''
    Model for an exercise image
    '''

    objects = SubmissionManager()
    '''Custom manager'''

    exercise = models.ForeignKey(Exercise,
                                 verbose_name=_('Exercise'))
    '''The exercise the image belongs to'''

    image = models.ImageField(verbose_name=_('Image'),
                              help_text=_('Only PNG and JPEG formats are supported'),
                              upload_to=exercise_image_upload_dir)
    '''Uploaded image'''

    is_main = models.BooleanField(verbose_name=_('Is main picture'),
                                  default=False,
                                  help_text=_("Tick the box if you want to set this image as the "
                                              "main one for the exercise (will be shown e.g. in "
                                              "the search). The first image is automatically "
                                              "marked by the system."))
    '''A flag indicating whether the image is the exercise's main image'''

    class Meta:
        '''
        Set default ordering
        '''
        ordering = ['-is_main', 'id']

    def save(self, *args, **kwargs):
        '''
        Only one image can be marked as main picture at a time
        '''
        if self.is_main:
            ExerciseImage.objects.filter(exercise=self.exercise).update(is_main=False)
            self.is_main = True
        else:
            if ExerciseImage.objects.accepted().filter(exercise=self.exercise).count() == 0 \
               or not ExerciseImage.objects.accepted() \
                            .filter(exercise=self.exercise, is_main=True)\
                            .count():
                self.is_main = True

        #
        # Reset all cached infos
        #
        for language in Language.objects.all():
            delete_template_fragment_cache('muscle-overview', language.id)
            delete_template_fragment_cache('exercise-overview', language.id)
            delete_template_fragment_cache('exercise-overview-mobile', language.id)
            delete_template_fragment_cache('equipment-overview', language.id)
            delete_template_fragment_cache('exercise-detail-header',
                                           self.exercise.id,
                                           language.id)
            delete_template_fragment_cache('exercise-detail-muscles',
                                           self.exercise.id,
                                           language.id)

        # And go on
        super(ExerciseImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''
        super(ExerciseImage, self).delete(*args, **kwargs)

        for language in Language.objects.all():
            delete_template_fragment_cache('muscle-overview', language.id)
            delete_template_fragment_cache('exercise-overview', language.id)
            delete_template_fragment_cache('exercise-overview-mobile', language.id)
            delete_template_fragment_cache('exercise-detail-header', self.exercise.id, language.id)
            delete_template_fragment_cache('exercise-detail-muscles', self.exercise.id, language.id)
            delete_template_fragment_cache('equipment-overview', language.id)

        # Make sure there is always a main image
        if not ExerciseImage.objects.accepted() \
                .filter(exercise=self.exercise, is_main=True).count() \
           and ExerciseImage.objects.accepted() \
                .filter(exercise=self.exercise) \
                .filter(is_main=False) \
                .count():

                image = ExerciseImage.objects.accepted() \
                    .filter(exercise=self.exercise, is_main=False)[0]
                image.is_main = True
                image.save()

    def get_owner_object(self):
        '''
        Image has no owner information
        '''
        return False

    def set_author(self, request):
        '''
        Set author and status

        This is only used when creating images (via web or API)
        '''
        if request.user.has_perm('exercises.add_exerciseimage'):
            self.status = self.STATUS_ACCEPTED
            if not self.license_author:
                self.license_author = 'wger.de'

        else:
            if not self.license_author:
                self.license_author = request.user.username

            subject = _('New user submitted image')
            message = _(u'The user {0} submitted a new image "{1}" for exercise {2}.').format(
                request.user.username,
                self.name,
                self.exercise)
            mail.mail_admins(six.text_type(subject),
                             six.text_type(message),
                             fail_silently=True)


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


# Generate thumbnails when uploading a new image
saved_file.connect(generate_aliases)


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

    def save(self, *args, **kwargs):
        '''
        Reset cached workouts
        '''
        for set in self.exercise.set_set.all():
            reset_workout_canonical_form(set.exerciseday.training_id)

        super(ExerciseComment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        '''
        Reset cached workouts
        '''
        for set in self.exercise.set_set.all():
            reset_workout_canonical_form(set.exerciseday.training.pk)

        super(ExerciseComment, self).delete(*args, **kwargs)

    def get_owner_object(self):
        '''
        Comment has no owner information
        '''
        return False
