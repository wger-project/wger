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
import random
# Standard library
import re

# Django
from django.contrib.auth.models import User


def generate_username_suggestions(username: str, count: int = 3):
    """
    Given a username, generates a list of available unique usernames.
    """
    text = re.sub(r'[^\w]', '', username) or 'user'

    candidates = [
        f'{text}{random.randint(1, 99)}',
        f'{text}{random.randint(100, 999)}',
        f'{text[0]}{text}{random.randint(1, 10)}',
        f'{text}{text[-1]}{random.randint(1, 10)}',
        f'{text}_{random.randint(1, 99)}',
    ]
    random.shuffle(candidates)

    taken = set(User.objects.filter(username__in=candidates).values_list('username', flat=True))

    return [c for c in candidates if c not in taken][:count]
