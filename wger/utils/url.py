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
from typing import (
    Dict,
    Optional,
)
from urllib.parse import (
    urlparse,
    urlunparse,
)

# Django
from django.conf import settings


def make_uri(
    path: str,
    id: Optional[int] = None,
    object_method: Optional[str] = None,
    query: Optional[Dict[str, any]] = None,
    server_url: str = settings.WGER_SETTINGS['WGER_INSTANCE'],
):
    uri_server = urlparse(server_url)
    query = query or {}
    path_list = [uri_server.path, 'api', 'v2', path]

    if id is not None:
        path_list.append(str(id))

    if object_method is not None:
        path_list.append(object_method)

    uri = urlunparse(
        (
            uri_server.scheme,
            uri_server.netloc,
            '/'.join(path_list) + '/',
            '',
            '&'.join([f'{key}={value}' for key, value in query.items()]),
            '',
        )
    )

    return uri
