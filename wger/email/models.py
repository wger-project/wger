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

from django.contrib.auth.models import User
from django.db import models

from wger.gym.models import Gym


class Log(models.Model):
    '''
    A log of a sent email
    '''

    class Meta:
        ordering = ["-date", ]

    date = models.DateField(auto_now=True)
    '''
    Date when the log was created
    '''

    user = models.ForeignKey(User,
                             editable=False)
    '''
    The user that created the email
    '''

    gym = models.ForeignKey(Gym,
                            editable=False,
                            related_name='email_log'
                            )
    '''
    Gym this log belongs to
    '''

    subject = models.CharField(max_length=100)
    '''
    The email subject
    '''

    body = models.TextField()
    '''
    The email body
    '''

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.subject


class CronEntry(models.Model):
    '''
    Simple list of emails to be sent by a cron job
    '''

    log = models.ForeignKey(Log,
                            editable=False)
    '''
    Foreign key to email log with subject and body
    '''

    email = models.EmailField()
    '''
    The email address
    '''

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.email
