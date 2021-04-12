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
import uuid

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import mail
from django.core.validators import MinLengthValidator
from django.db import models
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse
from django.utils import translation
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# Third Party
import bleach

# wger
from wger.core.models import Language
from wger.utils.cache import (
    delete_template_fragment_cache,
    reset_workout_canonical_form
)
from wger.utils.helpers import smart_capitalize
from wger.utils.managers import SubmissionManager
from wger.utils.models import (
    AbstractLicenseModel,
    AbstractSubmissionModel
)


logger = logging.getLogger(__name__)


class Muscle(models.Model):
    """
    Muscle an exercise works out
    """

    name = models.CharField(max_length=50,
                            verbose_name=_('Name'),
                            help_text=_('In latin, e.g. "Pectoralis major"'))

    # Whether to use the front or the back image for background
    is_front = models.BooleanField(default=1)

    # Metaclass to set some other properties
    class Meta:
        ordering = ["name", ]

    # Image to use when displaying this as a main muscle in an exercise
    @property
    def image_url_main(self):
        return static(f"images/muscles/main/muscle-{self.id}.svg")

    # Image to use when displaying this as a secondary muscle in an exercise
    @property
    def image_url_secondary(self):
        return static(f"images/muscles/secondary/muscle-{self.id}.svg")

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    def get_owner_object(self):
        """
        Muscle has no owner information
        """
        return False


class Equipment(models.Model):
    """
    Equipment used or needed by an exercise
    """

    name = models.CharField(max_length=50,
                            verbose_name=_('Name'))

    class Meta:
        """
        Set default ordering
        """
        ordering = ["name", ]

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    def get_owner_object(self):
        """
        Equipment has no owner information
        """
        return False


class ExerciseCategory(models.Model):
    """
    Model for an exercise category
    """
    name = models.CharField(max_length=100,
                            verbose_name=_('Name'),)

    # Metaclass to set some other properties
    class Meta:
        verbose_name_plural = _("Exercise Categories")
        ordering = ["name", ]

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    def get_owner_object(self):
        """
        Category has no owner information
        """
        return False

    def save(self, *args, **kwargs):
        """
        Reset all cached infos
        """

        super(ExerciseCategory, self).save(*args, **kwargs)

        # Cached template fragments
        for language in Language.objects.all():
            delete_template_fragment_cache('exercise-overview', language.id)

    def delete(self, *args, **kwargs):
        """
        Reset all cached infos
        """
        for language in Language.objects.all():
            delete_template_fragment_cache('exercise-overview', language.id)

        super(ExerciseCategory, self).delete(*args, **kwargs)


class Variation(models.Model):
    """
    Variation ids for exercises
    """

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'Variation {self.id}'

    def get_owner_object(self):
        """
        Variation has no owner information
        """
        return False


class ExerciseBase(AbstractSubmissionModel, AbstractLicenseModel, models.Model):
    """
    Model for an exercise base
    """

    objects = SubmissionManager()
    """Custom manager"""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='UUID')
    """Globally unique ID, to identify the base across installations"""

    category = models.ForeignKey(ExerciseCategory,
                                 verbose_name=_('Category'),
                                 on_delete=models.CASCADE)

    muscles = models.ManyToManyField(Muscle,
                                     blank=True,
                                     verbose_name=_('Primary muscles'))
    """Main muscles trained by the exercise"""

    muscles_secondary = models.ManyToManyField(Muscle,
                                               verbose_name=_('Secondary muscles'),
                                               related_name='secondary_muscles_base',
                                               blank=True)
    """Secondary muscles trained by the exercise"""

    equipment = models.ManyToManyField(Equipment,
                                       verbose_name=_('Equipment'),
                                       blank=True)
    """Equipment needed by this exercise"""

    variations = models.ForeignKey(Variation,
                                   verbose_name=_('Variations'),
                                   on_delete=models.CASCADE,
                                   null=True,
                                   blank=True)
    """Variations of this exercise"""

    #
    # Own methods
    #

    @property
    def get_languages(self):
        """
        Returns the languages from the exercises that use this base
        """
        return [exercise.language for exercise in self.exercises.all()]


class Exercise(AbstractSubmissionModel, AbstractLicenseModel, models.Model):
    """
    Model for an exercise
    """

    objects = SubmissionManager()
    """Custom manager"""

    description = models.TextField(max_length=2000,
                                   verbose_name=_('Description'),
                                   validators=[MinLengthValidator(40)])
    """Description on how to perform the exercise"""

    name = models.CharField(max_length=200,
                            verbose_name=_('Name'))
    """The exercise's name, with correct uppercase"""

    name_original = models.CharField(max_length=200,
                                     verbose_name=_('Name'),
                                     default='')
    """The exercise's name, as entered by the user"""

    creation_date = models.DateField(_('Date'),
                                     auto_now_add=True,
                                     null=True,
                                     blank=True)
    """The submission date"""

    language = models.ForeignKey(Language,
                                 verbose_name=_('Language'),
                                 on_delete=models.CASCADE)
    """The exercise's language"""

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='UUID')
    """Globally unique ID, to identify the exercise across installations"""

    exercise_base = models.ForeignKey(ExerciseBase,
                                      verbose_name='ExerciseBase',
                                      on_delete=models.CASCADE,
                                      default=None,
                                      null=True,
                                      related_name='exercises')
    """ Refers to the base exercise with non translated information """

    #
    # Django methods
    #
    class Meta:
        base_manager_name = 'objects'
        ordering = ["name", ]

    def get_absolute_url(self):
        """
        Returns the canonical URL to view an exercise
        """
        return reverse('exercise:exercise:view', kwargs={'id': self.id, 'slug': slugify(self.name)})

    def save(self, *args, **kwargs):
        """
        Reset all cached infos
        """
        self.name = smart_capitalize(self.name_original)
        super(Exercise, self).save(*args, **kwargs)

        # Cached template fragments
        for language in Language.objects.all():
            delete_template_fragment_cache('muscle-overview', language.id)
            delete_template_fragment_cache('exercise-overview', language.id)
            delete_template_fragment_cache('equipment-overview', language.id)

        # Cached workouts
        for setting in self.setting_set.all():
            reset_workout_canonical_form(setting.set.exerciseday.training_id)

    def delete(self, *args, **kwargs):
        """
        Reset all cached infos
        """

        # Cached template fragments
        for language in Language.objects.all():
            delete_template_fragment_cache('muscle-overview', language.id)
            delete_template_fragment_cache('exercise-overview', language.id)
            delete_template_fragment_cache('equipment-overview', language.id)

        # Cached workouts
        for setting in self.setting_set.all():
            reset_workout_canonical_form(setting.set.exerciseday.training.pk)

        super(Exercise, self).delete(*args, **kwargs)

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    #
    # Properties to expose the info from the exercise base
    #
    @property
    def category(self):
        return self.exercise_base.category

    @property
    def muscles(self):
        return self.exercise_base.muscles

    @property
    def muscles_secondary(self):
        return self.exercise_base.muscles_secondary

    @property
    def equipment(self):
        return self.exercise_base.equipment

    @property
    def images(self):
        return self.exercise_base.exerciseimage_set

    @property
    def variations(self):
        """
        Returns the variations for this exercise in the same language
        """
        out = []
        if self.exercise_base.variations:
            for variation in self.exercise_base.variations.exercisebase_set.all():
                for exercise in variation.exercises.filter(language=self.language).accepted():
                    out.append(exercise)
        return out

    #
    # Own methods
    #
    @property
    def main_image(self):
        """
        Return the main image for the exercise or None if nothing is found
        """
        return self.images.accepted().filter(is_main=True).first()

    @property
    def description_clean(self):
        """
        Return the exercise description with all markup removed
        """
        return bleach.clean(self.description, strip=True)

    def get_owner_object(self):
        """
        Exercise has no owner information
        """
        return False

    def send_email(self, request):
        """
        Sends an email after being successfully added to the database (for user
        submitted exercises only)
        """
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
                'url': url,
                'site': Site.objects.get_current().domain
            }
            message = render_to_string('exercise/email_new.tpl', context)
            mail.send_mail(subject,
                           message,
                           settings.WGER_SETTINGS['EMAIL_FROM'],
                           [user.email],
                           fail_silently=True)

    def set_author(self, request):
        """
        Set author and status
        This is only used when creating exercises (via web or API)
        """

        if request.user.has_perm('exercises.add_exercise'):
            self.status = self.STATUS_ACCEPTED
            if not self.license_author:
                self.license_author = request.get_host().split(':')[0]
        else:
            if not self.license_author:
                self.license_author = request.user.username

            subject = _('New user submitted exercise')

            message = _('The user {0} submitted a new exercise "{1}".').format(
                request.user.username, self.name_original)
            mail.mail_admins(str(subject),
                             str(message),
                             fail_silently=True)


def exercise_image_upload_dir(instance, filename):
    """
    Returns the upload target for exercise images
    """
    return "exercise-images/{0}/{1}".format(instance.exercise.id, filename)


class ExerciseImage(AbstractSubmissionModel, AbstractLicenseModel, models.Model):
    """
    Model for an exercise image
    """

    objects = SubmissionManager()
    """Custom manager"""

    uuid = models.UUIDField(default=uuid.uuid4,
                            editable=False,
                            verbose_name='UUID')
    """Globally unique ID, to identify the image across installations"""

    exercise = models.ForeignKey(ExerciseBase,
                                 verbose_name=_('Exercise'),
                                 on_delete=models.CASCADE)
    """The exercise the image belongs to"""

    image = models.ImageField(verbose_name=_('Image'),
                              help_text=_('Only PNG and JPEG formats are supported'),
                              upload_to=exercise_image_upload_dir)
    """Uploaded image"""

    is_main = models.BooleanField(verbose_name=_('Main picture'),
                                  default=False,
                                  help_text=_("Tick the box if you want to set this image as the "
                                              "main one for the exercise (will be shown e.g. in "
                                              "the search). The first image is automatically "
                                              "marked by the system."))
    """A flag indicating whether the image is the exercise's main image"""

    class Meta:
        """
        Set default ordering
        """
        ordering = ['-is_main', 'id']
        base_manager_name = 'objects'

    def save(self, *args, **kwargs):
        """
        Only one image can be marked as main picture at a time
        """
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

        # And go on
        super(ExerciseImage, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset all cached infos
        """
        super(ExerciseImage, self).delete(*args, **kwargs)

        for language in Language.objects.all():
            delete_template_fragment_cache('muscle-overview', language.id)
            delete_template_fragment_cache('exercise-overview', language.id)
            delete_template_fragment_cache('exercise-overview-mobile', language.id)
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
        """
        Image has no owner information
        """
        return False

    def set_author(self, request):
        """
        Set author and status
        This is only used when creating images (via web or API)
        """
        if request.user.has_perm('exercises.add_exerciseimage'):
            self.status = self.STATUS_ACCEPTED
            if not self.license_author:
                self.license_author = request.get_host().split(':')[0]

        else:
            if not self.license_author:
                self.license_author = request.user.username

            subject = _('New user submitted image')
            message = _('The user {0} submitted a new image "{1}" for exercise {2}.').format(
                request.user.username,
                self.name,
                self.exercise)
            mail.mail_admins(str(subject),
                             str(message),
                             fail_silently=True)


class ExerciseComment(models.Model):
    """
    Model for an exercise comment
    """
    exercise = models.ForeignKey(Exercise,
                                 verbose_name=_('Exercise'),
                                 editable=False,
                                 on_delete=models.CASCADE)
    comment = models.CharField(max_length=200,
                               verbose_name=_('Comment'),
                               help_text=_('A comment about how to correctly do this exercise.'))

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.comment

    def save(self, *args, **kwargs):
        """
        Reset cached workouts
        """
        for setting in self.exercise.setting_set.all():
            reset_workout_canonical_form(setting.set.exerciseday.training_id)

        super(ExerciseComment, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset cached workouts
        """
        for setting in self.exercise.setting_set.all():
            reset_workout_canonical_form(setting.set.exerciseday.training.pk)

        super(ExerciseComment, self).delete(*args, **kwargs)

    def get_owner_object(self):
        """
        Comment has no owner information
        """
        return False
