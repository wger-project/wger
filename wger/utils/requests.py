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

# Third Party
import requests

# wger
from wger import get_version


def wger_user_agent():
    return f'wger/{get_version()} - https://github.com/wger-project'


def wger_headers():
    return {'User-Agent': wger_user_agent()}


def get_all_paginated(url: str, headers=None):
    """
    Fetch all results from a paginated endpoint.

    :param url: The URL to fetch from.
    :param headers: Optional headers to send with the request.
    :return: A list of all results.
    """
    if headers is None:
        headers = {}

    results = []
    while True:
        response = requests.get(url, headers=headers).json()
        url = response['next']
        results.extend(response['results'])

        if not url:
            break
    return results


def get_paginated(url: str, headers=None):
    """
    Generator that iterates over a paginated endpoint

    :param url: The URL to fetch from.
    :param headers: Optional headers to send with the request.
    :return: Generator with the contents of the 'result' key
    """
    if headers is None:
        headers = {}

    while True:
        response = requests.get(url, headers=headers).json()

        for result in response['results']:
            yield result

        url = response['next']
        if not url:
            break
