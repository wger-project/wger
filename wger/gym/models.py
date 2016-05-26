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

import uuid
import datetime

from django.db import models as m
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext

from wger.gym.managers import GymManager


@python_2_unicode_compatible
class Gym(m.Model):
    '''
    Model for a gym
    '''

    class Meta:
        permissions = (
            ("gym_trainer", _("Trainer: can see the users for a gym")),
            ("manage_gym", _("Admin: can manage users for a gym")),
            ("manage_gyms", _("Admin: can administrate the different gyms")),
        )
        ordering = ["name", ]

    objects = GymManager()
    '''
    Custom Gym Query Manager
    '''

    name = m.CharField(max_length=60,
                       verbose_name=_('Name'))
    '''Gym name'''

    phone = m.CharField(verbose_name=_('Phone'),
                        max_length=20,
                        blank=True,
                        null=True)
    '''Phone number'''

    email = m.EmailField(verbose_name=_('Email'),
                         blank=True,
                         null=True)
    '''Email'''

    owner = m.CharField(verbose_name=_('Owner'),
                        max_length=100,
                        blank=True,
                        null=True)
    '''Gym owner'''

    zip_code = m.CharField(_(u'ZIP code'),
                           max_length=10,
                           blank=True,
                           null=True)
    '''ZIP code'''

    city = m.CharField(_(u'City'),
                       max_length=30,
                       blank=True,
                       null=True)
    '''City'''

    street = m.CharField(_(u'Street'),
                         max_length=30,
                         blank=True,
                         null=True)
    '''Street'''

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name

    def delete(self, using=None):
        '''
        Make sure that there are no users with this gym in their profiles
        '''

        # Not accessing the profile directly to avoid cyclic import problems
        for user in User.objects.filter(userprofile__gym=self).all():
            user.userprofile.gym = None
            user.userprofile.save()
        super(Gym, self).delete(using)

    def get_absolute_url(self):
        '''
        Return the URL for this object
        '''
        return reverse('gym:gym:user-list', kwargs={'pk': self.pk})

    def get_owner_object(self):
        '''
        Gym has no owner information
        '''
        return None


@python_2_unicode_compatible
class GymConfig(m.Model):
    '''
    Configuration options for a gym
    '''

    gym = m.OneToOneField(Gym,
                          related_name='config',
                          editable=False)
    '''
    Gym this configuration belongs to
    '''

    weeks_inactive = m.PositiveIntegerField(verbose_name=_('Reminder of inactive members'),
                                            help_text=_('Number of weeks since the last time a '
                                            'user logged his presence to be considered inactive'),
                                            default=4)
    '''
    Reminder of inactive members
    '''

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return ugettext(u'Configuration for {}'.format(self.gym.name))

    def get_owner_object(self):
        '''
        Config has no user owner
        '''
        return None


class AbstractGymUserConfigModel(m.Model):
    '''
    Abstract class for member and admin gym configuration models
    '''

    class Meta:
        abstract = True

    gym = m.ForeignKey(Gym,
                       editable=False)
    '''
    Gym this configuration belongs to
    '''

    user = m.OneToOneField(User,
                           editable=False)
    '''
    User this configuration belongs to
    '''


class GymAdminConfig(AbstractGymUserConfigModel, m.Model):
    '''
    Administrator/trainer configuration options for a specific gym
    '''

    class Meta:
        unique_together = ('gym', 'user')
        '''
        Only one entry per user and gym
        '''

    overview_inactive = m.BooleanField(verbose_name=_('Overview of inactive members'),
                                       help_text=_('Receive email overviews of inactive members'),
                                       default=True)
    '''
    Reminder of inactive members
    '''

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self


class GymUserConfig(AbstractGymUserConfigModel, m.Model):
    '''
    Gym member configuration options for a specific gym
    '''

    class Meta:
        unique_together = ('gym', 'user')
        '''
        Only one entry per user and gym
        '''

    include_inactive = m.BooleanField(verbose_name=_('Include in inactive overview'),
                                      help_text=_('Include this user in the email list with '
                                      'inactive members'),
                                      default=True)
    '''
    Include user in inactive overview
    '''

    def get_owner_object(self):
        '''
        While the model has a user foreign key, this is editable by all
        trainers in the gym.
        '''
        return None


class AdminUserNote(m.Model):
    '''
    Administrator notes about a member
    '''

    class Meta:
        '''
        Order by time
        '''
        ordering = ["-timestamp_created", ]

    user = m.ForeignKey(User,
                        editable=False,
                        related_name='adminusernote_user')
    '''
    User this note belongs to
    '''

    member = m.ForeignKey(User,
                          editable=False,
                          related_name='adminusernote_member')
    '''
    Gym member this note refers to
    '''

    timestamp_created = m.DateTimeField(auto_now_add=True)
    '''
    Time when this note was created
    '''

    timestamp_edited = m.DateTimeField(auto_now=True)
    '''
    Last time when this note was edited
    '''

    note = m.TextField(verbose_name=_('Note'))
    '''
    Actual note
    '''

    def get_owner_object(self):
        '''
        While the model has a user foreign key, this is editable by all
        trainers in the gym.
        '''
        return None


def gym_document_upload_dir(instance, filename):
    '''
    Returns the upload target for documents
    '''
    return "gym/documents/{0}/{1}/{2}".format(instance.member.userprofile.gym.id,
                                              instance.member.id,
                                              uuid.uuid4())


@python_2_unicode_compatible
class UserDocument(m.Model):
    '''
    Model for a document
    '''

    class Meta:
        '''
        Order by time
        '''
        ordering = ["-timestamp_created", ]

    user = m.ForeignKey(User,
                        editable=False,
                        related_name='userdocument_user')
    '''
    User this note belongs to
    '''

    member = m.ForeignKey(User,
                          editable=False,
                          related_name='userdocument_member')
    '''
    Gym member this note refers to
    '''

    timestamp_created = m.DateTimeField(auto_now_add=True)
    '''
    Time when this document was created
    '''

    timestamp_edited = m.DateTimeField(auto_now=True)
    '''
    Last time when this document was edited
    '''

    document = m.FileField(verbose_name=_('Document'),
                           upload_to=gym_document_upload_dir)
    '''
    Uploaded document
    '''

    original_name = m.CharField(max_length=128,
                                editable=False)
    '''
    Original document name when uploaded
    '''

    name = m.CharField(max_length=60,
                       verbose_name=_('Name'),
                       help_text=_('Will use file name if nothing provided'),
                       blank=True)
    '''
    Name or description
    '''

    note = m.TextField(verbose_name=_('Note'),
                       blank=True,
                       null=True)
    '''
    Note with additional information
    '''

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        if self.name != self.original_name:
            return "{} ({})".format(self.name, self.original_name)
        else:
            return "{}".format(self.name)

    def get_owner_object(self):
        '''
        While the model has a user foreign key, this is editable by all
        trainers in the gym.
        '''
        return None


@python_2_unicode_compatible
class ContractType(m.Model):
    '''
    Model for a contract's type

    A contract type is a user-editable way of enhancing the contract to
    specify types, such as e.g. 'with personal trainer', 'regular', etc.
    '''

    class Meta:
        '''
        Order by name
        '''
        ordering = ["name", ]

    gym = m.ForeignKey(Gym,
                       editable=False)
    '''
    The gym this contract type belongs to
    '''

    name = m.CharField(verbose_name=_('Name'),
                       max_length=25)
    '''
    The contract type's short name
    '''

    description = m.TextField(verbose_name=_('Description'),
                              blank=True,
                              null=True)
    '''
    Free text field for additional information
    '''

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return u"{}".format(self.name)

    def get_owner_object(self):
        '''
        Contract type has no owner information
        '''
        return None


@python_2_unicode_compatible
class ContractOption(m.Model):
    '''
    Model for a contract Option

    A contract option is a user-editable way of enhancing the contract to
    specify options, such as e.g. 'cash', 'bank withdrawal', etc. The
    difference with a contract type is that a contract can only be of one
    type but can have different options.
    '''

    class Meta:
        '''
        Order by name
        '''
        ordering = ["name", ]

    gym = m.ForeignKey(Gym,
                       editable=False)
    '''
    The gym this contract option belongs to
    '''

    name = m.CharField(verbose_name=_('Name'),
                       max_length=25)
    '''
    The contract options short name
    '''

    description = m.TextField(verbose_name=_('Description'),
                              blank=True,
                              null=True)
    '''
    Free text field for additional information
    '''

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return u"{}".format(self.name)

    def get_owner_object(self):
        '''
        Contract type has no owner information
        '''
        return None


@python_2_unicode_compatible
class Contract(m.Model):
    '''
    Model for a member's contract in a gym
    '''

    AMOUNT_TYPE_YEARLY = '1'
    AMOUNT_TYPE_HALFYEARLY = '2'
    AMOUNT_TYPE_MONTHLY = '3'
    AMOUNT_TYPE_BIWEEKLY = '4'
    AMOUNT_TYPE_WEEKLY = '5'
    AMOUNT_TYPE_DAILY = '6'

    AMOUNT_TYPE = (
        (AMOUNT_TYPE_YEARLY, _("Yearly")),
        (AMOUNT_TYPE_HALFYEARLY, _('Half yearly')),
        (AMOUNT_TYPE_MONTHLY, _('Monthly')),
        (AMOUNT_TYPE_BIWEEKLY, _('Biweekly')),
        (AMOUNT_TYPE_WEEKLY, _('Weekly')),
        (AMOUNT_TYPE_DAILY, _('Daily')),
    )

    class Meta:
        '''
        Order by time
        '''
        ordering = ["-date_start", ]

    user = m.ForeignKey(User,
                        editable=False,
                        related_name='contract_user')
    '''
    User that originally created the contract
    '''

    member = m.ForeignKey(User,
                          editable=False,
                          related_name='contract_member')
    '''
    Gym member this contract refers to
    '''

    timestamp_created = m.DateTimeField(auto_now_add=True)
    '''
    Time when the contract was created
    '''

    timestamp_edited = m.DateTimeField(auto_now=True)
    '''
    Last time when the contract was edited
    '''

    contract_type = m.ForeignKey(ContractType,
                                 blank=True,
                                 null=True,
                                 verbose_name=_('Contract type'))
    '''
    Optional type of contract
    '''

    options = m.ManyToManyField(ContractOption,
                                verbose_name=_('Options'),
                                blank=True)
    '''
    Options for the contract
    '''

    amount = m.DecimalField(verbose_name=_('Amount'),
                            decimal_places=2,
                            max_digits=12,
                            default=0)
    '''
    The amount to pay
    '''

    payment = m.CharField(verbose_name=_('Payment type'),
                          max_length=2,
                          choices=AMOUNT_TYPE,
                          default=AMOUNT_TYPE_MONTHLY,
                          help_text=_('How often the amount will be charged to the member'))
    '''
    How often the amount will be charged to the member
    '''

    is_active = m.BooleanField(verbose_name=_('Contract is active'),
                               default=True)
    '''
    Flag showing whether the contract is currently active
    '''

    date_start = m.DateField(verbose_name=_('Start date'),
                             default=datetime.date.today,
                             blank=True,
                             null=True)
    '''
    The date when the contract starts
    '''

    date_end = m.DateField(verbose_name=_('End date'),
                           blank=True,
                           null=True)
    '''
    The date when the contract ends
    '''

    email = m.EmailField(verbose_name=_('Email'),
                         blank=True,
                         null=True)
    '''The member's email'''

    zip_code = m.CharField(_(u'ZIP code'),
                           max_length=10,
                           blank=True,
                           null=True)
    '''ZIP code'''

    city = m.CharField(_(u'City'),
                       max_length=30,
                       blank=True,
                       null=True)
    '''City'''

    street = m.CharField(_(u'Street'),
                         max_length=30,
                         blank=True,
                         null=True)
    '''Street'''

    phone = m.CharField(verbose_name=_('Phone'),
                        max_length=20,
                        blank=True,
                        null=True)
    '''Phone number'''

    profession = m.CharField(verbose_name=_('Profession'),
                             max_length=50,
                             blank=True,
                             null=True)
    '''
    The member's profession
    '''

    note = m.TextField(verbose_name=_('Note'),
                       blank=True,
                       null=True)
    '''
    Free text note with additional information
    '''

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return "#{}".format(self.id)

    def get_absolute_url(self):
        '''
        Return the URL for this object
        '''
        return reverse('gym:contract:view', kwargs={'pk': self.pk})

    def get_owner_object(self):
        '''
        While the model has a user foreign key, this is editable by all
        managers in the gym.
        '''
        return None
