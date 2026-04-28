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
import logging

# Django
from django.conf import settings
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
)
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.urls import reverse_lazy
from django.utils.translation import (
    gettext as _,
    gettext_lazy,
)
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
)

# wger
from wger.nutrition.api.filtersets import IngredientFilterSet
from wger.nutrition.forms import (
    IngredientForm,
    UnitChooserForm,
)
from wger.nutrition.models import Ingredient
from wger.utils.cache import cache_mapper
from wger.utils.constants import PAGINATION_OBJECTS_PER_PAGE
from wger.utils.generic_views import (
    WgerDeleteMixin,
    WgerFormMixin,
)
from wger.utils.language import load_language


logger = logging.getLogger(__name__)


# ************************
# Ingredient functions
# ************************
class IngredientListView(ListView):
    """
    Show an overview of all ingredients using cursor-based pagination.

    This is more efficient than OFFSET-based pagination for large lists because it
    can use an index on id to jump directly to the next page, while OFFSET
    requires scanning and counting rows up to the offset.

    This also allows to keep the list public so that crawlers can index it

    The query string interface:
        - no parameter           -> first page
        - ?after=<id>            -> rows with id > <id>, ascending
    """

    model = Ingredient
    template_name = 'ingredient/overview.html'
    context_object_name = 'ingredients_list'
    paginate_by = None  # disabled — cursor handled in get_context_data
    filterset_class = IngredientFilterSet

    PAGE_SIZE = PAGINATION_OBJECTS_PER_PAGE

    def get_queryset(self):
        """
        Apply language + filterset, then cursor logic. We fetch one extra row
        beyond PAGE_SIZE so we know whether a next page exists without an
        extra COUNT query.
        """
        language = load_language()
        queryset = Ingredient.objects.filter(language=language)
        filterset = self.filterset_class(self.request.GET or None, queryset=queryset)
        qs = filterset.qs.order_by('id')

        after = self.request.GET.get('after')
        if after:
            try:
                qs = qs.filter(id__gt=int(after))
            except (TypeError, ValueError):
                # fall through to first page
                pass

        return qs[: self.PAGE_SIZE + 1]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ingredients = list(context['ingredients_list'])

        # We fetched PAGE_SIZE + 1 to peek at the next-page existence.
        has_next = len(ingredients) > self.PAGE_SIZE
        if has_next:
            ingredients = ingredients[: self.PAGE_SIZE]

        # Pre-build the pagination URLs here
        next_url = None
        if has_next and ingredients:
            params = self.request.GET.copy()
            params['after'] = str(ingredients[-1].id)
            next_url = f'?{params.urlencode()}'

        is_paginated = bool(self.request.GET.get('after'))
        first_url = None
        if is_paginated:
            params = self.request.GET.copy()
            params.pop('after', None)
            first_url = f'?{params.urlencode()}' if params else '?'

        context['ingredients_list'] = ingredients
        context['has_next'] = has_next
        context['next_url'] = next_url
        context['first_url'] = first_url
        context['is_paginated'] = is_paginated

        return context


def view(request, pk, slug=None):
    context = {}

    ingredient = cache.get(cache_mapper.get_ingredient_key(int(pk)))
    if not ingredient:
        ingredient = get_object_or_404(Ingredient, pk=pk)
        cache.set(
            cache_mapper.get_ingredient_key(ingredient),
            ingredient,
            settings.WGER_SETTINGS['INGREDIENT_CACHE_TTL'],
        )

    context['ingredient'] = ingredient
    context['image'] = ingredient.get_image(request)
    context['form'] = UnitChooserForm(
        data={'ingredient_id': ingredient.id, 'amount': 100, 'unit': None}
    )

    return render(request, 'ingredient/view.html', context)


class IngredientDeleteView(
    WgerDeleteMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    DeleteView,
):
    """
    Generic view to delete an existing ingredient
    """

    model = Ingredient
    template_name = 'delete.html'
    success_url = reverse_lazy('nutrition:ingredient:list')
    messages = gettext_lazy('Successfully deleted')
    permission_required = 'nutrition.delete_ingredient'

    # Send some additional data to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['title'] = _('Delete {0}?').format(self.object)
        return context


class IngredientEditView(WgerFormMixin, LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """
    Generic view to update an existing ingredient
    """

    template_name = 'form.html'
    model = Ingredient
    form_class = IngredientForm
    permission_required = 'nutrition.change_ingredient'

    def get_context_data(self, **kwargs):
        """
        Send some additional data to the template
        """
        context = super().get_context_data(**kwargs)
        context['title'] = _('Edit {0}').format(self.object)
        return context


class IngredientCreateView(WgerFormMixin, CreateView):
    """
    Generic view to add a new ingredient
    """

    template_name = 'form.html'
    model = Ingredient
    form_class = IngredientForm
    title = gettext_lazy('Add a new ingredient')

    def form_valid(self, form):
        form.instance.language = load_language()
        form.instance.set_author(self.request)
        return super(IngredientCreateView, self).form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        """
        Demo users can't submit ingredients
        """
        if request.user.userprofile.is_temporary:
            return HttpResponseForbidden()
        return super(IngredientCreateView, self).dispatch(request, *args, **kwargs)
