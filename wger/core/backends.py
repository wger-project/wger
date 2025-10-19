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
import logging

# Django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend


logger = logging.getLogger(__name__)
User = get_user_model()


class AuthProxyUserBackend(BaseBackend):
    """
    Authenticates against a username passed in the request meta (header).
    Relies on the middleware to ensure the header comes from a trusted source.
    """

    def authenticate(
        self,
        request,
        username: str | None = None,
        email: str | None = None,
        name: str | None = None,
    ):
        """
        Authenticate the user based on the username provided.
        The middleware ensures this is only called when the source is trusted.
        """
        if not username:
            # This backend requires a username passed explicitly
            return None

        create_unknown_user = getattr(settings, 'AUTH_PROXY_CREATE_UNKNOWN_USER', False)

        user = None
        try:
            user = User.objects.get(username=username)
            logger.debug(f"AuthProxy: Found existing user '{username}'")
        except User.DoesNotExist:
            if create_unknown_user:
                try:
                    user = User.objects.create_user(username=username, email=email, first_name=name)
                    logger.info(f"AuthProxy: Created new user '{username}'")
                except Exception as e:
                    logger.error(f"AuthProxy: Failed to create user '{username}': {e}")
                    return None
            else:
                logger.warning(
                    f"AuthProxy: User '{username}' not found and auto-creation is disabled."
                )
                return None
        except Exception as e:
            logger.error(f"AuthProxy: Error fetching user '{username}': {e}")
            return None

        return user

    def get_user(self, user_id):
        """
        Standard Django method to retrieve a user by ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
