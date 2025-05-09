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

# Django
from django.contrib.auth.views import redirect_to_login
from django.views.generic import TemplateView


class ReactView(TemplateView):
    """
    ReactView is a TemplateView that renders a React page.

    To get the corresponding React component, check "src/routes.tsx"
    """

    template_name = 'react/react-page.html'
    div_id = 'react-page'
    login_required = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['div_id'] = self.div_id
        context['hide_title_and_options'] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        """
        Only logged-in users are allowed to access this page
        """
        if self.login_required and not request.user.is_authenticated:
            return redirect_to_login(request.path)

        return super().dispatch(request, *args, **kwargs)
