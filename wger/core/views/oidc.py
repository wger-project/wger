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
from dataclasses import dataclass

# Django
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import (
    Http404,
    HttpResponseRedirect,
)
from django.shortcuts import render
from django.template.context_processors import csrf
from django.urls import reverse
from django.utils.translation import gettext as _

# Third Party
from allauth.idp.oidc.adapter import get_adapter
from allauth.idp.oidc.models import Token

# wger
from wger.utils.oidc_auth import is_provider_configured


# What counts as a live connection. An authorization code is a step in the flow,
# not a grant.
GRANT_TOKEN_TYPES = (Token.Type.ACCESS_TOKEN, Token.Type.REFRESH_TOKEN)


@dataclass
class ConnectedApplication:
    """One application a user has granted access to, as the page shows it.

    No "connected since": rotation deletes the old refresh token and writes a
    new one, so ``created_at`` is the last refresh, not the consent.
    """

    client_id: str
    name: str
    permissions: list[str]
    #: When the longest-lived token runs out, if nothing refreshes it.
    expires_at: datetime.datetime | None


def scope_labels(scopes: list[str]) -> list[str]:
    """
    The wording the consent screen used, so the two pages cannot drift apart
    """
    display = get_adapter().scope_display
    return [str(display.get(scope, scope)) for scope in scopes]


def connected_applications(user) -> list[ConnectedApplication]:
    """
    The applications ``user`` has granted access to, one entry per client

    Expired tokens are left out: housekeeping only deletes them once a day.
    """
    tokens = (
        Token.objects.valid()
        .filter(user=user, type__in=GRANT_TOKEN_TYPES, client__isnull=False)
        .select_related('client')
    )

    by_client: dict[str, list[Token]] = {}
    for token in tokens:
        by_client.setdefault(token.client_id, []).append(token)

    applications = []
    for client_tokens in by_client.values():
        # An access token can be minted for a subset of what was granted, so
        # what the application can do is the union over its tokens.
        scopes: list[str] = []
        for token in client_tokens:
            scopes.extend(s for s in token.get_scopes() if s not in scopes)

        expiries = [token.expires_at for token in client_tokens]
        applications.append(
            ConnectedApplication(
                client_id=client_tokens[0].client_id,
                name=client_tokens[0].client.name,
                permissions=scope_labels(scopes),
                # A token without an expiry outlives every other one.
                expires_at=None if None in expiries else max(expiries),
            )
        )

    return sorted(applications, key=lambda a: a.name.lower())


@login_required
def overview(request):
    """
    Applications the user has given access to their account, and a way to take
    it back
    """
    if not is_provider_configured():
        raise Http404('The OAuth2 provider is not configured')

    context = {}
    context.update(csrf(request))

    client_id = request.POST.get('disconnect') if request.method == 'POST' else None
    if client_id:
        # Scoped to the user, so another user's client id matches nothing
        tokens = Token.objects.filter(user=request.user, client_id=client_id)
        token = tokens.select_related('client').first()
        if token is not None:
            name = token.client.name
            # Every type, not just GRANT_TOKEN_TYPES: a pending authorization
            # code would still be exchangeable for a fresh token.
            tokens.delete()
            messages.success(request, _('{name} no longer has access').format(name=name))
        return HttpResponseRedirect(reverse('core:user:connected-applications'))

    context['applications'] = connected_applications(request.user)

    return render(request, 'user/connected_applications.html', context)
