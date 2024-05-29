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

# Standard Library
import datetime
import decimal
import json
import logging
import os
import random
import string
from functools import wraps

# Django
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes
from django.utils.http import (
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)


logger = logging.getLogger(__name__)


class EmailAuthBackend:
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
            return None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


class DecimalJsonEncoder(json.JSONEncoder):
    """
    Custom JSON encoder.

    This class is needed because we store some data as a decimal (e.g. the
    individual weight entries in the workout log) and they need to be
    processed, json.dumps() doesn't work on them
    """

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        if isinstance(obj, datetime.date):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def disable_for_loaddata(signal_handler):
    """
    Decorator to prevent clashes when loading data with loaddata and
    post_connect signals. See also:
    http://stackoverflow.com/questions/3499791/how-do-i-prevent-fixtures-from-conflicting
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs['raw']:
            return
        signal_handler(*args, **kwargs)

    return wrapper


def next_weekday(date, weekday):
    """
    Helper function to find the next weekday after a given date,
    e.g. the first Monday after the 2013-12-05

    See link for more details:
    * http://stackoverflow.com/questions/6558535/python-find-the-date-for-the-first-monday-after-a

    :param date: the start date
    :param weekday: weekday (0, Monday, 1 Tuesday, 2 Wednesday)
    :type date: datetime.date
    :type weekday int
    :return: datetime.date
    """
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)


def make_uid(input):
    """
    Small wrapper to generate a UID, usually used in URLs to allow for
    anonymous access
    """
    return urlsafe_base64_encode(force_bytes(input))


def make_token(user):
    """
    Convenience function that generates the UID and token for a user

    :param user: a user object
    :return: the uid and the token
    """
    uid = make_uid(user.pk)
    token = default_token_generator.make_token(user)

    return uid, token


def check_token(uidb64, token):
    """
    Checks that the user token is correct.

    :param uidb:
    :param token:
    :return: True on success, False in all other situations
    """
    if uidb64 is not None and token is not None:
        try:
            uid = int(urlsafe_base64_decode(uidb64))
        except ValueError as e:
            logger.info(f'Could not decode UID: {e}')
            return False

        try:
            user = User.objects.get(pk=uid)
            if user is not None and default_token_generator.check_token(user, token):
                return True

        except User.DoesNotExist:
            return False

    return False


def password_generator(length=15):
    """
    A simple password generator

    Also removes some 'problematic' characters like O and 0
    :param length: the length of the password
    :return: the generated password
    """
    chars = string.ascii_letters + string.digits
    random.seed = os.urandom(1024)
    for char in ('I', '1', 'l', 'O', '0', 'o'):
        chars = chars.replace(char, '')

    return ''.join(random.choice(chars) for i in range(length))


def check_access(request_user, username=None):
    """
    Small helper function to check that the current (possibly unauthenticated)
    user can access a URL that the owner user shared the link.

    Raises Http404 in case of error (no read-only access allowed)

    :param request_user: the user in the current request
    :param username: the username
    :return: a tuple: (is_owner, user)
    """

    if username:
        user = get_object_or_404(User, username=username)
        if request_user.username == username:
            user = request_user
        elif not user.userprofile.ro_access:
            raise Http404('You are not allowed to access this page.')

    # If there is no user_pk, just show the user his own data
    else:
        if not request_user.is_authenticated:
            raise Http404('You are not allowed to access this page.')
        user = request_user

    is_owner = request_user == user
    return is_owner, user


def normalize_decimal(d):
    """
    Normalizes a decimal input

    This simply performs a more "human" normalization, since python's decimal
    normalize() converts "100" into "1e2", which is not a format usually used
    when writing workout plans.

    :param d: decimal to convert
    :return: normalized decimal
    """
    normalized = d.normalize()
    sign, digits, exponent = normalized.as_tuple()
    if exponent > 0:
        return decimal.Decimal((sign, digits + (0,) * exponent, 0))
    else:
        return normalized


def random_string(length=32):
    """
    Generates a random string
    """
    return ''.join(random.choice(string.ascii_uppercase) for i in range(length))


class BaseImage:
    def save_image(self, retrieved_image, json_data: dict):
        # Save the downloaded image
        # http://stackoverflow.com/questions/1308386/programmatically-saving-image-to
        if os.name == 'nt':
            img_temp = NamedTemporaryFile()
        else:
            img_temp = NamedTemporaryFile(delete=True)
        img_temp.write(retrieved_image.content)
        img_temp.flush()

        self.image.save(
            os.path.basename(json_data['image']),
            File(img_temp),
        )

    @classmethod
    def from_json(cls, connect_to, retrieved_image, json_data: dict, generate_uuid: bool = False):
        image: cls = cls()
        if not generate_uuid:
            image.uuid = json_data['uuid']
        return image
