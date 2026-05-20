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
    Any,
    Dict,
    Optional,
)
from urllib.parse import (
    urljoin,
    urlparse,
    urlunparse,
)

# Django
from django.conf import settings
from django.http import HttpRequest


def make_uri(
    path: str,
    object_id: Optional[int] = None,
    object_method: Optional[str] = None,
    query: Optional[Dict[str, Any]] = None,
    server_url: str = settings.WGER_SETTINGS['WGER_INSTANCE'],
):
    uri_server = urlparse(server_url)
    query = query or {}
    path_list = [uri_server.path, 'api', 'v2', path]

    if object_id is not None:
        path_list.append(str(object_id))

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


def make_absolute_url(path: Optional[str], request: Optional[HttpRequest] = None) -> Optional[str]:
    """
    Return an absolute URL for a path.

    When a request is available the URL is built from it, so the host the client
    connected to is preserved. When there is no request, e.g. while the exercise
    cache is warmed by a celery task, the URL is built from settings.SITE_URL.
    Empty paths are returned unchanged. Paths that are already absolute pass
    through untouched, since neither build_absolute_uri nor urljoin alter them.
    """
    if not path:
        return path

    if request is not None:
        return request.build_absolute_uri(path)

    if site_url := getattr(settings, 'SITE_URL', None):
        return urljoin(site_url, path)

    return path
