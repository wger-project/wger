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
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout,
)
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

# wger
from wger.utils.helpers import remove_language_code


logger = logging.getLogger(__name__)
User = get_user_model()


class AuthProxyHeaderMiddleware(MiddlewareMixin):
    """
    Middleware to authenticate users based on a header set by a trusted proxy.

    Relies on settings:
    - AUTH_PROXY_HEADER: The request.META key containing the username.
    - AUTH_PROXY_TRUSTED_IPS: List of IPs allowed to set the header.
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.login_url_path = remove_language_code(reverse('core:user:login'))

    def process_request(self, request):
        header_key = getattr(settings, 'AUTH_PROXY_HEADER', None)
        user_email_key = getattr(settings, 'AUTH_PROXY_USER_EMAIL_HEADER', None)
        user_name_key = getattr(settings, 'AUTH_PROXY_USER_NAME_HEADER', None)
        trusted_ips = set(getattr(settings, 'AUTH_PROXY_TRUSTED_IPS', []))

        # Skip processing if not configured
        if not header_key or not trusted_ips:
            # logger.debug(
            #     'AuthProxyMiddleware: AUTH_PROXY_HEADER or AUTH_PROXY_TRUSTED_IPS not configured.'
            # )
            return None

        # Only handle requests to the login page.
        # Here the user will be logged in using the proxy headers and redirected to the original page.
        if remove_language_code(request.path_info) != self.login_url_path:
            # logger.debug(f'AuthProxyMiddleware: not request to login page. Skipping.')
            return None

        # Get the client IP address.
        # Use REMOTE_ADDR as it's the direct connection IP (should be the proxy).
        client_ip = request.META.get('REMOTE_ADDR')

        # Check if the request comes from a trusted IP
        if not client_ip or client_ip not in trusted_ips:
            # If the header *is* present but the IP is not trusted, log a warning
            # as this might indicate a misconfiguration or security probing.
            if header_key in request.META:
                logger.warning(
                    f"AuthProxyMiddleware: Header '{header_key}' received from "
                    f"untrusted IP '{client_ip}'. Ignoring header."
                )
            # Not a trusted IP, do nothing.
            return None

        username = request.META.get(header_key)
        email = request.META.get(user_email_key, '') if user_email_key else None
        name = request.META.get(user_name_key, '') if user_name_key else None
        if not username:
            # Trusted IP, but no header. Could mean proxy auth failed upstream.
            # Log, but otherwise do nothing.
            logger.debug(
                f"AuthProxyMiddleware: No username found in header '{header_key}' from "
                f"trusted IP '{client_ip}'."
            )

            return None

        # If user is already authenticated and matches the header, do nothing.
        if request.user.is_authenticated:
            if request.user.get_username() == username:
                return None

            # Logged in as someone else? This shouldn't usually happen if the
            # proxy is forcing the user, but we should log out the old session
            # and log in the header user for consistency.
            else:
                logger.warning(
                    f"AuthProxyMiddleware: User mismatch. Session user '{request.user.get_username()}' "
                    f"differs from proxy header user '{username}'. Logging out old user."
                )
                logout(request)

        # Authenticate using our custom backend
        user = authenticate(request, username=username, email=email, name=name)

        if user:
            # Authentication successful, log the user in.
            login(request, user)
            logger.info(
                f"AuthProxyMiddleware: User '{username}' authenticated via header from "
                f"trusted IP '{client_ip}'."
            )
            next_url = request.GET.get('next', reverse('core:dashboard'))
            if request.user.is_authenticated:
                return redirect(next_url)
        else:
            # Authentication failed (e.g., user couldn't be found/created by backend)
            logger.error(
                f"AuthProxyMiddleware: Authentication failed for username '{username}' "
                f"from header '{header_key}' (Trusted IP: {client_ip})."
            )

            # Explicitly clear any potentially lingering user object
            request.user = None

        return None
