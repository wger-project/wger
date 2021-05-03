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
import datetime
import logging
import typing

# Django
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import (
    ObjectDoesNotExist,
    ValidationError
)
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import (
    DaysOfWeek,
    RepetitionUnit,
    WeightUnit
)
from wger.exercises.models import Exercise
from wger.utils.cache import (
    cache_mapper,
    reset_workout_canonical_form,
    reset_workout_log
)
from wger.utils.fields import Html5DateField
from wger.utils.helpers import normalize_decimal


logger = logging.getLogger(__name__)

RIR_OPTIONS = [(None, '------'),
               ('0', 0),
               ('0.5', 0.5),
               ('1', 1),
               ('1.5', 1.5),
               ('2', 2),
               ('2.5', 2.5),
               ('3', 3),
               ('3.5', 3.5),
               ('4', 4)]


#
# Classes
#
class Workout(models.Model):
    """
    Model for a training schedule
    """

    class Meta:
        """
        Meta class to set some other properties
        """
        ordering = ["-creation_date", ]

    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    comment = models.CharField(verbose_name=_('Description'),
                               max_length=100,
                               blank=True,
                               help_text=_("A short description or goal of the workout. For "
                                           "example 'Focus on back' or 'Week 1 of program xy'."))
    user = models.ForeignKey(User, verbose_name=_('User'), on_delete=models.CASCADE)

    def get_absolute_url(self):
        """
        Returns the canonical URL to view a workout
        """
        return reverse('manager:workout:view', kwargs={'pk': self.id})

    def __str__(self):
        """
        Return a more human-readable representation
        """
        if self.comment:
            return "{0}".format(self.comment)
        else:
            return "{0} ({1})".format(_('Workout'), self.creation_date)

    def save(self, *args, **kwargs):
        """
        Reset all cached infos
        """
        reset_workout_canonical_form(self.id)
        super(Workout, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset all cached infos
        """
        reset_workout_canonical_form(self.id)
        super(Workout, self).delete(*args, **kwargs)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    @property
    def canonical_representation(self):
        """
        Returns a canonical representation of the workout

        This form makes it easier to cache and use everywhere where all or part
        of a workout structure is needed. As an additional benefit, the template
        caches are not needed anymore.
        """
        workout_canonical_form = cache.get(cache_mapper.get_workout_canonical(self.pk))
        if not workout_canonical_form:
            day_canonical_repr = []
            muscles_front = []
            muscles_back = []
            muscles_front_secondary = []
            muscles_back_secondary = []

            # Sort list by weekday
            day_list = [i for i in self.day_set.select_related()]
            day_list.sort(key=lambda day: day.get_first_day_id)

            for day in day_list:
                canonical_repr_day = day.get_canonical_representation()

                # Collect all muscles
                for i in canonical_repr_day['muscles']['front']:
                    if i not in muscles_front:
                        muscles_front.append(i)
                for i in canonical_repr_day['muscles']['back']:
                    if i not in muscles_back:
                        muscles_back.append(i)
                for i in canonical_repr_day['muscles']['frontsecondary']:
                    if i not in muscles_front_secondary:
                        muscles_front_secondary.append(i)
                for i in canonical_repr_day['muscles']['backsecondary']:
                    if i not in muscles_back_secondary:
                        muscles_back_secondary.append(i)

                day_canonical_repr.append(canonical_repr_day)

            workout_canonical_form = {'obj': self,
                                      'muscles': {'front': muscles_front,
                                                  'back': muscles_back,
                                                  'frontsecondary': muscles_front_secondary,
                                                  'backsecondary': muscles_back_secondary},
                                      'day_list': day_canonical_repr}
            # Save to cache
            cache.set(cache_mapper.get_workout_canonical(self.pk), workout_canonical_form)

        return workout_canonical_form


class ScheduleManager(models.Manager):
    """
    Custom manager for workout schedules
    """

    def get_current_workout(self, user):
        """
        Finds the currently active workout for the user, by checking the schedules
        and the workouts
        :rtype : list
        """

        # Try first to find an active schedule that has steps
        try:
            schedule = Schedule.objects.filter(user=user).get(is_active=True)
            if schedule.schedulestep_set.count():
                # The schedule might exist and have steps, but if it's too far in
                # the past and is not a loop, we won't use it. Doing it like this
                # is kind of wrong, but lets us continue to the correct place
                if not schedule.get_current_scheduled_workout():
                    raise ObjectDoesNotExist

                active_workout = schedule.get_current_scheduled_workout().workout
            else:
                # same as above
                raise ObjectDoesNotExist

        # there are no active schedules, just return the last workout
        except ObjectDoesNotExist:

            schedule = False
            try:
                active_workout = Workout.objects.filter(user=user).latest('creation_date')

            # no luck, there aren't even workouts for the user
            except ObjectDoesNotExist:
                active_workout = False

        return (active_workout, schedule)


class Schedule(models.Model):
    """
    Model for a workout schedule.

    A schedule is a collection of workous that are done for a certain time.
    E.g. workouts A, B, C, A, B, C, and so on.
    """

    objects = ScheduleManager()
    """Custom manager"""

    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             editable=False,
                             on_delete=models.CASCADE)
    """
    The user this schedule belongs to. This could be accessed through a step
    that points to a workout, that points to a user, but this is more straight
    forward and performant
    """

    name = models.CharField(verbose_name=_('Name'),
                            max_length=100,
                            help_text=_("Name or short description of the schedule. "
                                        "For example 'Program XYZ'."))
    """Name or short description of the schedule."""

    start_date = Html5DateField(verbose_name=_('Start date'),
                                default=datetime.date.today)
    """The start date of this schedule"""

    is_active = models.BooleanField(verbose_name=_('Schedule active'),
                                    default=True,
                                    help_text=_("Tick the box if you want to mark this schedule "
                                                "as your active one (will be shown e.g. on your "
                                                "dashboard). All other schedules will then be "
                                                "marked as inactive"))
    """A flag indicating whether the schedule is active (needed for dashboard)"""

    is_loop = models.BooleanField(verbose_name=_('Is a loop'),
                                  default=False,
                                  help_text=_("Tick the box if you want to repeat the schedules "
                                              "in a loop (i.e. A, B, C, A, B, C, and so on)"))
    """A flag indicating whether the schedule should act as a loop"""

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    def get_absolute_url(self):
        return reverse('manager:schedule:view', kwargs={'pk': self.id})

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    def save(self, *args, **kwargs):
        """
        Only one schedule can be marked as active at a time
        """
        if self.is_active:
            Schedule.objects.filter(user=self.user).update(is_active=False)
            self.is_active = True

        super(Schedule, self).save(*args, **kwargs)

    def get_current_scheduled_workout(self):
        """
        Returns the currently active schedule step for a user
        """
        steps = self.schedulestep_set.all()
        start_date = self.start_date
        found = False
        if not steps:
            return False
        while not found:
            for step in steps:
                current_limit = start_date + datetime.timedelta(weeks=step.duration)
                if current_limit >= datetime.date.today():
                    found = True
                    return step
                start_date = current_limit

            # If it's not a loop, there's no workout that matches, return
            if not self.is_loop:
                return False

    def get_end_date(self):
        """
        Calculates the date when the schedule is over or None is the schedule
        is a loop.
        """
        if self.is_loop:
            return None

        end_date = self.start_date
        for step in self.schedulestep_set.all():
            end_date = end_date + datetime.timedelta(weeks=step.duration)
        return end_date


class ScheduleStep(models.Model):
    """
    Model for a step in a workout schedule.

    A step is basically a workout a with a bit of metadata (next and previous
    steps, duration, etc.)
    """

    class Meta:
        """
        Set default ordering
        """
        ordering = ["order", ]

    schedule = models.ForeignKey(Schedule,
                                 verbose_name=_('schedule'),
                                 on_delete=models.CASCADE)
    """The schedule is step belongs to"""

    workout = models.ForeignKey(Workout, on_delete=models.CASCADE)
    """The workout this step manages"""

    duration = models.IntegerField(verbose_name=_('Duration'),
                                   help_text=_('The duration in weeks'),
                                   default=4,
                                   validators=[MinValueValidator(1), MaxValueValidator(25)])
    """The duration in weeks"""

    order = models.IntegerField(verbose_name=_('Order'),
                                default=1)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.workout

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.workout.comment

    def get_dates(self):
        """
        Calculate the start and end date for this step
        """

        steps = self.schedule.schedulestep_set.all()
        start_date = end_date = self.schedule.start_date
        previous = 0

        if not steps:
            return False

        for step in steps:
            start_date += datetime.timedelta(weeks=previous)
            end_date += datetime.timedelta(weeks=step.duration)
            previous = step.duration

            if step == self:
                return start_date, end_date


class Day(models.Model):
    """
    Model for a training day
    """

    training = models.ForeignKey(Workout,
                                 verbose_name=_('Workout'), on_delete=models.CASCADE)
    description = models.CharField(max_length=100,
                                   verbose_name=_('Description'),
                                   help_text=_('A description of what is done on this day (e.g. '
                                               '"Pull day") or what body parts are trained (e.g. '
                                               '"Arms and abs")'))
    day = models.ManyToManyField(DaysOfWeek,
                                 verbose_name=_('Day'))

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.description

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.training

    @property
    def get_first_day_id(self):
        """
        Return the PK of the first day of the week, this is used in the template
        to order the days in the template
        """
        return self.day.all()[0].pk

    def save(self, *args, **kwargs):
        """
        Reset all cached infos
        """

        reset_workout_canonical_form(self.training_id)
        super(Day, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset all cached infos
        """

        reset_workout_canonical_form(self.training_id)
        super(Day, self).delete(*args, **kwargs)

    @property
    def canonical_representation(self):
        """
        Return the canonical representation for this day

        This is extracted from the workout representation because that one is cached
        and this isn't.
        """
        for i in self.training.canonical_representation['day_list']:
            if int(i['obj'].pk) == int(self.pk):
                return i

    def get_canonical_representation(self):
        """
        Creates a canonical representation for this day
        """
        canonical_repr = []
        muscles_front = []
        muscles_back = []
        muscles_front_secondary = []
        muscles_back_secondary = []

        for set_obj in self.set_set.select_related():
            exercise_tmp = []

            for exercise in set_obj.exercises:
                setting_tmp = []
                exercise_images_tmp = []

                # Muscles for this set
                for muscle in exercise.muscles.all():
                    if muscle.is_front and muscle not in muscles_front:
                        muscles_front.append(muscle)
                    elif not muscle.is_front and muscle not in muscles_back:
                        muscles_back.append(muscle)

                for muscle in exercise.muscles_secondary.all():
                    if muscle.is_front and muscle not in muscles_front:
                        muscles_front_secondary.append(muscle)
                    elif not muscle.is_front and muscle.id not in muscles_back:
                        muscles_back_secondary.append(muscle)

                for setting in Setting.objects.filter(set=set_obj,
                                                      exercise=exercise).order_by('order', 'id'):
                    setting_tmp.append(setting)

                # "Smart" textual representation
                setting_text = set_obj.reps_smart_text(exercise)

                # Exercise comments
                comment_list = []
                for i in exercise.exercisecomment_set.all():
                    comment_list.append(i.comment)

                # Flag indicating whether any of the settings has saved weight
                has_weight = False
                for i in setting_tmp:
                    if i.weight:
                        has_weight = True
                        break

                # Collect exercise images
                for image in exercise.images.all():
                    exercise_images_tmp.append({'image': image.image.url,
                                                'is_main': image.is_main,
                                                })

                # Put it all together
                exercise_tmp.append({'obj': exercise,
                                     'setting_obj_list': setting_tmp,
                                     'setting_text': setting_text,
                                     'has_weight': has_weight,
                                     'comment_list': comment_list,
                                     'image_list': exercise_images_tmp})

            # If it's a superset, check that all exercises have the same repetitions.
            # If not, just take the smallest number and drop the rest, because otherwise
            # it doesn't make sense

            # if len(exercise_tmp) > 1:
            #     common_reps = 100
            #     for exercise in exercise_tmp:
            #         if len(exercise['setting_list']) < common_reps:
            #             common_reps = len(exercise['setting_list'])

            #     for exercise in exercise_tmp:
            #         if len(exercise['setting_list']) > common_reps:
            #             exercise['setting_list'].pop(-1)
            #             exercise['setting_obj_list'].pop(-1)
            #             setting_text, setting_list = set_obj.reps_smart_text(exercise)
            #             exercise['setting_text'] = setting_text

            canonical_repr.append({'obj': set_obj,
                                   'exercise_list': exercise_tmp,
                                   'is_superset': True if len(exercise_tmp) > 1 else False,
                                   'settings_computed': set_obj.compute_settings,
                                   'muscles': {
                                       'back': muscles_back,
                                       'front': muscles_front,
                                       'frontsecondary': muscles_front_secondary,
                                       'backsecondary': muscles_front_secondary
                                   }})

        # Days of the week
        tmp_days_of_week = []
        for day_of_week in self.day.select_related():
            tmp_days_of_week.append(day_of_week)

        return {'obj': self,
                'days_of_week': {
                    'text': ', '.join([str(_(i.day_of_week)) for i in tmp_days_of_week]),
                    'day_list': tmp_days_of_week},
                'muscles': {
                    'back': muscles_back,
                    'front': muscles_front,
                    'frontsecondary': muscles_front_secondary,
                    'backsecondary': muscles_front_secondary
                },
                'set_list': canonical_repr}


class Set(models.Model):
    """
    Model for a set of exercises
    """
    DEFAULT_SETS = 4
    MAX_SETS = 10

    exerciseday = models.ForeignKey(Day,
                                    verbose_name=_('Exercise day'),
                                    on_delete=models.CASCADE)
    order = models.IntegerField(blank=True,
                                null=True,
                                verbose_name=_('Order'))
    sets = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(MAX_SETS)],
                               verbose_name=_('Number of sets'),
                               default=DEFAULT_SETS)

    # Metaclass to set some other properties
    class Meta:
        ordering = ["order", ]

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return "Set-ID {0}".format(self.id)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.exerciseday.training

    def save(self, *args, **kwargs):
        """
        Reset all cached infos
        """

        reset_workout_canonical_form(self.exerciseday.training_id)
        super(Set, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset all cached infos
        """

        reset_workout_canonical_form(self.exerciseday.training_id)
        super(Set, self).delete(*args, **kwargs)

    @property
    def exercises(self) -> typing.List[Exercise]:
        """Returns the exercises for this set"""
        return list(dict.fromkeys([s.exercise for s in self.setting_set.all()]))

    @property
    def compute_settings(self):  # -> typing.List[Setting]:
        """
        Compute the synthetic settings for this set.

        If we have super sets the result will be an interleaved list of
        settings so the result are the exercises that have to be done, in
        order, e.g.:

        * Exercise 1, 10 reps, 50 kg
        * Exercise 2, 8 reps,  10 kg
        * Exercise 1, 10 reps, 50 kg
        * Exercise 2, 8 reps,  10 kg
        """
        setting_lists = []
        for exercise in self.exercises:
            setting_lists.append(self.computed_settings_exercise(exercise))

        # Interleave all lists
        return [val for tup in zip(*setting_lists) for val in tup]

    def computed_settings_exercise(self, exercise: Exercise):  # -> typing.List[Setting]
        """
        Returns a computed list of settings

        If a set has only one set
        """
        settings = self.setting_set.filter(exercise=exercise)

        if settings.count() == 0:
            return[]
        elif settings.count() == 1:
            setting = settings.first()
            return [setting] * self.sets
        else:
            return list(settings.all())

    def reps_smart_text(self, exercise: Exercise):
        """
        "Smart" textual representation

        This is a human representation of the settings, in a way that humans
        would also write: e.g. "8 8 10 10" but "4 x 10" and not "10 10 10 10".
        This helper also takes care to process, hide or show the different repetition
        and weight units as appropriate, e.g. "8 x 2 Plates", "10, 20, 30, ∞"

        :param exercise:
        :return setting_text, setting_list:
        """

        def get_rir_representation(setting):
            """
            Returns the representation for the Reps-In-Reserve for a setting
            """

            if setting.rir:
                rir = f"{setting.rir} RiR"
            else:
                rir = ""
            return rir

        def get_reps_reprentation(setting, rep_unit):
            """
            Returns the representation for the repetitions for a setting

            This is basically just to allow for a special representation for the
            "Until Failure" unit
            """
            if setting.repetition_unit_id != 2:
                reps = "{0} {1}".format(setting.reps, rep_unit).strip()
            else:
                reps = '∞'
            return reps

        def get_weight_unit_reprentation(setting):
            """
            Returns the representation for the weight unit for a setting

            This is basically just to allow for a special representation for the
            "Repetition" and "Until Failure" unit
            """
            if setting.repetition_unit.id not in (1, 2):
                rep_unit = _(setting.repetition_unit.name)
            else:
                rep_unit = ''
            return rep_unit

        def normalize_weight(setting):
            """
            The weight can be None, or a decimal. In that case, normalize so
            that we don't return e.g. '15.00', but always '15', independently of
            the database used.
            """
            if setting.weight:
                weight = normalize_decimal(setting.weight)
            else:
                weight = setting.weight
            return weight

        def get_setting_text(current_setting, multi=False):
            """Gets the repetition text for a complete setting"""
            rep_unit = get_weight_unit_reprentation(current_setting)
            reps = get_reps_reprentation(current_setting, rep_unit)
            weight_unit = settings[0].weight_unit.name
            weight = normalize_weight(current_setting)
            rir = get_rir_representation(current_setting)
            out = '{0} × {1}'.format(self.sets, reps).strip() if not multi else reps
            if weight:
                rir_text = f', {rir}' if rir else ''
                out += f' ({weight} {weight_unit}{rir_text})'
            else:
                out += ' ({0})'.format(rir) if rir else ''

            return out

        settings = self.setting_set.filter(exercise=exercise)
        setting_text = ''

        # Only one setting entry, this is a "compact" representation such as e.g.
        # 4x10 or similar
        if len(settings) == 1:
            setting = settings[0]
            setting_text = get_setting_text(setting)

        # There's more than one setting, each set can have a different combination
        # of repetitions, weight, etc. e.g. 10, 8, 8, 12
        elif len(settings) > 1:
            tmp_reps_text = []
            for setting in settings:
                tmp_reps_text.append(get_setting_text(setting, multi=True))

            setting_text = ' – '.join(tmp_reps_text)

        return setting_text


class Setting(models.Model):
    """
    Settings for an exercise (weight, reps, etc.)
    """

    set = models.ForeignKey(Set, verbose_name=_('Sets'), on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise,
                                 verbose_name=_('Exercises'),
                                 on_delete=models.CASCADE)
    repetition_unit = models.ForeignKey(RepetitionUnit,
                                        verbose_name=_('Unit'),
                                        default=1,
                                        on_delete=models.CASCADE)
    """
    The repetition unit of a set. This can be e.g. a repetition, a minute, etc.
    """

    reps = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(600)],
                               verbose_name=_('Reps'))
    """
    Amount of repetitions, minutes, etc. for a set.

    Note that since adding the unit field, the name is no longer correct, but is
    kept for compatibility reasons (specially for the REST API).
    """

    weight = models.DecimalField(verbose_name=_('Weight'),
                                 max_digits=6,
                                 decimal_places=2,
                                 blank=True,
                                 null=True,
                                 validators=[MinValueValidator(0), MaxValueValidator(1500)])
    """Planed weight for the repetitions"""

    weight_unit = models.ForeignKey(WeightUnit,
                                    verbose_name=_('Unit'),
                                    default=1,
                                    on_delete=models.CASCADE)
    """
    The weight unit of a set. This can be e.g. kg, lb, km/h, etc.
    """

    rir = models.CharField(verbose_name=_('RiR'),
                           max_length=3,
                           blank=True,
                           null=True,
                           choices=RIR_OPTIONS)
    """
    Reps in reserve, RiR. The amount of reps that could realistically still be
    done in the set.
    """

    order = models.IntegerField(blank=True,
                                verbose_name=_('Order'))
    comment = models.CharField(max_length=100,
                               blank=True,
                               verbose_name=_('Comment'))

    # Metaclass to set some other properties
    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f"setting {self.id} for exercise {self.exercise_id} in set {self.set_id}"

    def save(self, *args, **kwargs):
        """
        Reset cache
        """
        reset_workout_canonical_form(self.set.exerciseday.training_id)

        # If the user selected "Until Failure", do only 1 "repetition",
        # everythin else doesn't make sense.
        if self.repetition_unit == 2:
            self.reps = 1
        super(Setting, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset cache
        """

        reset_workout_canonical_form(self.set.exerciseday.training_id)
        super(Setting, self).delete(*args, **kwargs)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.set.exerciseday.training


class WorkoutLog(models.Model):
    """
    A log entry for an exercise
    """

    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             editable=False,
                             on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise,
                                 verbose_name=_('Exercise'),
                                 on_delete=models.CASCADE)
    workout = models.ForeignKey(Workout,
                                verbose_name=_('Workout'),
                                on_delete=models.CASCADE)

    repetition_unit = models.ForeignKey(RepetitionUnit,
                                        verbose_name=_('Unit'),
                                        default=1,
                                        on_delete=models.CASCADE)
    """
    The unit of the log. This can be e.g. a repetition, a minute, etc.
    """

    reps = models.IntegerField(verbose_name=_('Repetitions'),
                               validators=[MinValueValidator(0)])
    """
    Amount of repetitions, minutes, etc.

    Note that since adding the unit field, the name is no longer correct, but is
    kept for compatibility reasons (specially for the REST API).
    """

    weight = models.DecimalField(decimal_places=2,
                                 max_digits=5,
                                 verbose_name=_('Weight'),
                                 validators=[MinValueValidator(0)])

    weight_unit = models.ForeignKey(WeightUnit,
                                    verbose_name=_('Unit'),
                                    default=1,
                                    on_delete=models.CASCADE)
    """
    The weight unit of the log. This can be e.g. kg, lb, km/h, etc.
    """

    date = Html5DateField(verbose_name=_('Date'))

    rir = models.CharField(verbose_name=_('RiR'),
                           max_length=3,
                           blank=True,
                           null=True,
                           choices=RIR_OPTIONS)
    """
    Reps in reserve, RiR. The amount of reps that could realistically still be
    done in the set.
    """

    # Metaclass to set some other properties
    class Meta:
        ordering = ["date", "reps"]

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return "Log entry: {0} - {1} kg on {2}".format(self.reps,
                                                       self.weight,
                                                       self.date)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    def get_workout_session(self, date=None):
        """
        Returns the corresponding workout session

        :return the WorkoutSession object or None if nothing was found
        """
        if not date:
            date = self.date

        try:
            return WorkoutSession.objects.filter(user=self.user).get(date=date)
        except WorkoutSession.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        """
        Reset cache
        """
        reset_workout_log(self.user_id, self.date.year, self.date.month, self.date.day)

        # If the user selected "Until Failure", do only 1 "repetition",
        # everythin else doesn't make sense.
        if self.repetition_unit == 2:
            self.reps = 1
        super(WorkoutLog, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset cache
        """
        reset_workout_log(self.user_id, self.date.year, self.date.month, self.date.day)
        super(WorkoutLog, self).delete(*args, **kwargs)


class WorkoutSession(models.Model):
    """
    Model for a workout session
    """

    # Note: values hardcoded in manager.helpers.WorkoutCalendar
    IMPRESSION_BAD = '1'
    IMPRESSION_NEUTRAL = '2'
    IMPRESSION_GOOD = '3'

    IMPRESSION = (
        (IMPRESSION_BAD, _("Bad")),
        (IMPRESSION_NEUTRAL, _('Neutral')),
        (IMPRESSION_GOOD, _('Good')),
    )

    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             on_delete=models.CASCADE)
    """
    The user the workout session belongs to

    See note in weight.models.WeightEntry about why this is not editable=False
    """

    workout = models.ForeignKey(Workout,
                                verbose_name=_('Workout'),
                                on_delete=models.CASCADE)
    """
    The workout the session belongs to
    """

    date = Html5DateField(verbose_name=_('Date'))
    """
    The date the workout session was performed
    """

    notes = models.TextField(verbose_name=_('Notes'),
                             null=True,
                             blank=True,
                             help_text=_('Any notes you might want to save about this workout '
                                         'session.'))
    """
    User notes about the workout
    """

    impression = models.CharField(verbose_name=_('General impression'),
                                  max_length=2,
                                  choices=IMPRESSION,
                                  default=IMPRESSION_NEUTRAL,
                                  help_text=_('Your impression about this workout session. '
                                              'Did you exercise as well as you could?'))
    """
    The user's general impression of workout
    """

    time_start = models.TimeField(verbose_name=_('Start time'),
                                  blank=True,
                                  null=True)
    """
    Time the workout session started
    """

    time_end = models.TimeField(verbose_name=_('Finish time'),
                                blank=True,
                                null=True)
    """
    Time the workout session ended
    """

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return "{0} - {1}".format(self.workout, self.date)

    class Meta:
        """
        Set other properties
        """
        ordering = ["date", ]
        unique_together = ("date", "user")

    def clean(self):
        """
        Perform some additional validations
        """

        if (not self.time_end and self.time_start) or (self.time_end and not self.time_start):
            raise ValidationError(_("If you enter a time, you must enter both start and end time."))

        if self.time_end and self.time_start and self.time_start > self.time_end:
            raise ValidationError(_("The start time cannot be after the end time."))

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    def save(self, *args, **kwargs):
        """
        Reset cache
        """
        reset_workout_log(self.user_id, self.date.year, self.date.month)
        super(WorkoutSession, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Reset cache
        """
        reset_workout_log(self.user_id, self.date.year, self.date.month)
        super(WorkoutSession, self).delete(*args, **kwargs)
