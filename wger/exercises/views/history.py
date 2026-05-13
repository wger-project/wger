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
# You should have received a copy of the GNU Affero General Public License

# Standard Library
import logging
from datetime import timedelta

# Django
from django import forms
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import (
    EmptyPage,
    PageNotAnInteger,
    Paginator,
)
from django.db.models import (
    Q,
    QuerySet,
)
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

# Third Party
import django_filters
from actstream import action as actstream_action
from actstream.models import Action

# wger
from wger.exercises.views.helper import StreamVerbs


logger = logging.getLogger(__name__)


PAGE_SIZE = 50

# Models that the history view exposes as filter options. Each tuple is
# (filter key, app_label, model name).
TRACKED_MODELS = (
    ('exercise', 'exercises', 'exercise'),
    ('translation', 'exercises', 'translation'),
    ('image', 'exercises', 'exerciseimage'),
    ('video', 'exercises', 'exercisevideo'),
    ('comment', 'exercises', 'exercisecomment'),
    ('alias', 'exercises', 'alias'),
)

# Bootstrap badge variant per tracked model
BADGE_CLASS_BY_MODEL = {
    'exercise': 'text-bg-success',
    'translation': 'text-bg-primary',
    'image': 'text-bg-info',
    'video': 'text-bg-danger',
    'comment': 'text-bg-warning',
    'alias': 'text-bg-secondary',
}

NEW_CONTRIBUTOR_DAYS = 60
"""
Edits made by accounts younger than this are visually flagged so admins can
review them more carefully (watchlist concept).
"""


def _content_type_map():
    """
    Return a dict mapping the filter key (e.g. ``'translation'``) to its
    ContentType. Looked up once per request.
    """
    result = {}
    for key, app_label, model in TRACKED_MODELS:
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model)
        except ContentType.DoesNotExist:
            continue
        result[key] = ct
    return result


class ActionHistoryFilter(django_filters.FilterSet):
    MODEL_CHOICES = [(key, key.capitalize()) for key, *_ in TRACKED_MODELS]
    VERB_CHOICES = [(v.value, v.value.capitalize()) for v in StreamVerbs]

    user = django_filters.CharFilter(
        method='filter_user',
        label=_('User'),
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
    )
    model_type = django_filters.ChoiceFilter(
        choices=MODEL_CHOICES,
        method='filter_model_type',
        label=_('Type'),
        empty_label=_('All'),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    verb = django_filters.ChoiceFilter(
        field_name='verb',
        choices=VERB_CHOICES,
        label=_('Action'),
        empty_label=_('All'),
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'}),
    )
    date_from = django_filters.DateFilter(
        field_name='timestamp',
        lookup_expr='date__gte',
        label=_('From'),
        widget=forms.DateInput(
            attrs={'class': 'form-control form-control-sm', 'type': 'date'},
        ),
    )
    date_to = django_filters.DateFilter(
        field_name='timestamp',
        lookup_expr='date__lte',
        label=_('To'),
        widget=forms.DateInput(
            attrs={'class': 'form-control form-control-sm', 'type': 'date'},
        ),
    )

    class Meta:
        model = Action
        fields = ['user', 'model_type', 'verb', 'date_from', 'date_to']

    def filter_user(self, queryset: QuerySet, name: str, value: str):
        if not value:
            return queryset
        user_ct = ContentType.objects.get_for_model(User)
        # ``actor_object_id`` is a CharField in actstream (generic FK), but
        # ``User.pk`` is an integer. Postgres rejects the implicit cast, so the
        # subquery is materialized and stringified here.
        user_pks = User.objects.filter(
            username__icontains=value,
        ).values_list('pk', flat=True)
        return queryset.filter(
            actor_content_type=user_ct,
            actor_object_id__in=[str(pk) for pk in user_pks],
        )

    def filter_model_type(self, queryset: QuerySet, name: str, value: str):
        ct_map = _content_type_map()
        if value in ct_map:
            # Also include DELETED events for this type, where action_object is
            # gone and the model is recorded in ``data.model_type`` instead.
            return queryset.filter(
                Q(action_object_content_type=ct_map[value])
                | Q(verb=StreamVerbs.DELETED.value, data__model_type=value)
            )
        return queryset


@permission_required('exercises.change_exercise')
def control(request: HttpRequest) -> HttpResponse:
    """
    Admin view of the history of the exercises
    """

    ct_map = _content_type_map()
    # Inverse mapping used for cheap template lookups without hitting the DB again.
    ct_id_to_key = {ct.id: key for key, ct in ct_map.items()}
    tracked_ct_ids = [ct.id for ct in ct_map.values()]

    # Include events tied to a tracked exercise model via action_object, plus
    # DELETED events that no longer have an action_object (the original was
    # deleted) but recorded their model in ``data.model_type``.
    tracked_filter = Q(action_object_content_type__in=tracked_ct_ids) | Q(
        verb=StreamVerbs.DELETED.value,
        data__model_type__in=[key for key, *_ in TRACKED_MODELS],
    )

    base_queryset = (
        Action.objects.select_related(
            'actor_content_type',
            'action_object_content_type',
            'target_content_type',
        )
        .filter(tracked_filter)
        .order_by('-timestamp')
    )

    action_filter = ActionHistoryFilter(request.GET, queryset=base_queryset)

    now = timezone.now()
    stats_base = Action.objects.filter(tracked_filter)
    stats = {
        'last_24h': stats_base.filter(timestamp__gte=now - timedelta(days=1)).count(),
        'last_7d': stats_base.filter(timestamp__gte=now - timedelta(days=7)).count(),
        'last_30d': stats_base.filter(timestamp__gte=now - timedelta(days=30)).count(),
    }

    paginator = Paginator(action_filter.qs, PAGE_SIZE)
    page_number = request.GET.get('page', 1)
    try:
        page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page = paginator.page(1)

    # Bulk-load the actor users for this page
    user_ct = ContentType.objects.get_for_model(User)
    actor_ids = {
        int(entry.actor_object_id)
        for entry in page.object_list
        if entry.actor_content_type_id == user_ct.id and entry.actor_object_id
    }
    actor_map = {u.pk: u for u in User.objects.filter(pk__in=actor_ids)}
    new_contributor_cutoff = now - timedelta(days=NEW_CONTRIBUTOR_DAYS)

    out = []
    for entry in page.object_list:
        actor = (
            actor_map.get(int(entry.actor_object_id))
            if entry.actor_content_type_id == user_ct.id and entry.actor_object_id
            else None
        )
        is_new_contributor = bool(
            actor and actor.date_joined and actor.date_joined >= new_contributor_cutoff
        )

        model_key = ct_id_to_key.get(entry.action_object_content_type_id)
        # DELETED events have no action_object — the model type is carried in
        # ``data.model_type`` instead.
        if not model_key and entry.verb == StreamVerbs.DELETED.value and entry.data:
            model_key = entry.data.get('model_type')

        data = {
            'verb': entry.verb,
            'stream': entry,
            'model_key': model_key,
            'badge_class': BADGE_CLASS_BY_MODEL.get(model_key, 'text-bg-light'),
            'is_new_contributor': is_new_contributor,
            'object_missing': False,
        }

        if entry.verb == StreamVerbs.UPDATED.value:
            entry_obj = entry.action_object
            if entry_obj is None or not hasattr(entry_obj, 'history'):
                # The underlying object has been deleted (or doesn't track
                # history), render a placeholder row
                data['object_missing'] = entry_obj is None
            else:
                try:
                    historical_entry = entry_obj.history.as_of(entry.timestamp)._history
                except (entry_obj.__class__.DoesNotExist, AttributeError, ValueError):
                    # No history snapshot exists at that timestamp (e.g. because the
                    # row predates history tracking).
                    historical_entry = None

                if historical_entry is not None:
                    previous_entry = historical_entry.prev_record
                    data['id'] = historical_entry.id
                    data['content_type_id'] = entry.action_object_content_type_id
                    if previous_entry:
                        data['delta'] = historical_entry.diff_against(previous_entry)
                        data['history_id'] = previous_entry.history_id

        out.append(data)

    # GET parameters without ``page`` so pagination links keep filters intact.
    qs_no_page = request.GET.copy()
    qs_no_page.pop('page', None)
    querystring = qs_no_page.urlencode()

    return render(
        request,
        'history/overview.html',
        {
            'context': out,
            'filter': action_filter,
            'page_obj': page,
            'paginator': paginator,
            'is_paginated': page.has_other_pages(),
            'querystring': querystring,
            'stats': stats,
            # We can't pass the enum to the template, so we have to do this
            # https://stackoverflow.com/questions/35953132/
            'verbs': StreamVerbs.__members__,
        },
    )


@require_POST
@permission_required('exercises.change_exercise')
def history_revert(request, history_pk, content_type_id):
    """
    Used to revert history objects
    """
    object_type = get_object_or_404(ContentType, pk=content_type_id)
    object_class = object_type.model_class()
    history = object_class.history.get(history_id=history_pk)
    history.instance.save()

    actstream_action.send(
        request.user,
        verb=StreamVerbs.UPDATED.value,
        action_object=history.instance,
        info='reverted history by admin',
    )

    return HttpResponseRedirect(reverse('exercise:history:overview'))
