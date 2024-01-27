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

# Django
from django.conf.urls import include
from django.contrib.auth import views
from django.urls import (
    path,
    re_path,
)
from django.views.generic import TemplateView

# wger
from wger.core.forms import UserLoginForm
from wger.core.views import (
    languages,
    license,
    misc,
    repetition_units,
    user,
    weight_units,
)


# sub patterns for languages
patterns_language = [
    path(
        'list',
        languages.LanguageListView.as_view(),
        name='overview',
    ),
    path(
        '<int:pk>/view',
        languages.LanguageDetailView.as_view(),
        name='view',
    ),
    path(
        '<int:pk>/delete',
        languages.LanguageDeleteView.as_view(),
        name='delete',
    ),
    path(
        '<int:pk>/edit',
        languages.LanguageEditView.as_view(),
        name='edit',
    ),
    path(
        'add',
        languages.LanguageCreateView.as_view(),
        name='add',
    ),
]

# sub patterns for user
patterns_user = [
    path(
        'login',
        views.LoginView.as_view(template_name='user/login.html', authentication_form=UserLoginForm),
        name='login',
    ),
    path('logout', user.logout, name='logout'),
    path('delete', user.delete, name='delete'),
    path('<int:user_pk>/delete', user.delete, name='delete'),
    path('confirm-email', user.confirm_email, name='confirm-email'),
    path('<int:user_pk>/trainer-login', user.trainer_login, name='trainer-login'),
    path('registration', user.registration, name='registration'),
    path('preferences', user.preferences, name='preferences'),
    path('api-key', user.api_key, name='api-key'),
    path('demo-entries', misc.demo_entries, name='demo-entries'),
    path('<int:pk>/activate', user.UserActivateView.as_view(), name='activate'),
    path('<int:pk>/deactivate', user.UserDeactivateView.as_view(), name='deactivate'),
    path('<int:pk>/edit', user.UserEditView.as_view(), name='edit'),
    path('<int:pk>/overview', user.UserDetailView.as_view(), name='overview'),
    path('list', user.UserListView.as_view(), name='list'),
    # Password reset is implemented by Django, no need to cook our own soup here
    # (besides the templates)
    path(
        'password/change',
        user.WgerPasswordChangeView.as_view(),
        name='change-password',
    ),
    path(
        'password/reset/',
        user.WgerPasswordResetView.as_view(),
        name='password_reset',
    ),
    path(
        'password/reset/done/',
        views.PasswordResetDoneView.as_view(),
        name='password_reset_done',
    ),
    re_path(
        r'^password/reset/check/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,33})$',
        user.WgerPasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        'password/reset/complete/',
        views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),
]

# sub patterns for licenses
patterns_license = [
    path(
        'license/list',
        license.LicenseListView.as_view(),
        name='list',
    ),
    path(
        'license/add',
        license.LicenseAddView.as_view(),
        name='add',
    ),
    path(
        'license/<int:pk>/edit',
        license.LicenseUpdateView.as_view(),
        name='edit',
    ),
    path(
        'license/<int:pk>/delete',
        license.LicenseDeleteView.as_view(),
        name='delete',
    ),
]

# sub patterns for setting units
patterns_repetition_units = [
    path(
        'list',
        repetition_units.ListView.as_view(),
        name='list',
    ),
    path(
        'add',
        repetition_units.AddView.as_view(),
        name='add',
    ),
    path(
        '<int:pk>/edit',
        repetition_units.UpdateView.as_view(),
        name='edit',
    ),
    path(
        '<int:pk>/delete',
        repetition_units.DeleteView.as_view(),
        name='delete',
    ),
]

# sub patterns for setting units
patterns_weight_units = [
    path(
        'list',
        weight_units.ListView.as_view(),
        name='list',
    ),
    path(
        'add',
        weight_units.AddView.as_view(),
        name='add',
    ),
    path(
        '<int:pk>)/edit',
        weight_units.UpdateView.as_view(),
        name='edit',
    ),
    path(
        '<int:pk>/delete',
        weight_units.DeleteView.as_view(),
        name='delete',
    ),
]

#
# Actual patterns
#
urlpatterns = [
    # The landing page
    path('', misc.index, name='index'),
    # The dashboard
    path('dashboard', misc.dashboard, name='dashboard'),
    # Others
    path(
        'imprint',
        TemplateView.as_view(template_name='misc/about.html'),
        name='imprint',
    ),
    path(
        'feedback',
        misc.FeedbackClass.as_view(),
        name='feedback',
    ),
    path('language/', include((patterns_language, 'language'), namespace='language')),
    path('user/', include((patterns_user, 'user'), namespace='user')),
    path('license/', include((patterns_license, 'license'), namespace='license')),
    path(
        'repetition-unit/',
        include((patterns_repetition_units, 'repetition-unit'), namespace='repetition-unit'),
    ),
    path('weight-unit/', include((patterns_weight_units, 'weight-unit'), namespace='weight-unit')),
]
