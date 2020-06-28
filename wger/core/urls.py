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
from django.conf.urls import (
    include,
    url
)
from django.contrib.auth import views
from django.urls import reverse_lazy
from django.views.generic import TemplateView

# wger
from wger.core.forms import UserLoginForm
from wger.core.views import (
    languages,
    license,
    misc,
    repetition_units,
    user,
    weight_units
)


# sub patterns for languages
patterns_language = [
    url(r'^list$',
        languages.LanguageListView.as_view(),
        name='overview'),
    url(r'^(?P<pk>\d+)/view$',
        languages.LanguageDetailView.as_view(),
        name='view'),
    url(r'^(?P<pk>\d+)/delete$',
        languages.LanguageDeleteView.as_view(),
        name='delete'),
    url(r'^(?P<pk>\d+)/edit',
        languages.LanguageEditView.as_view(),
        name='edit'),
    url(r'^add$',
        languages.LanguageCreateView.as_view(),
        name='add'),
]

# sub patterns for user
patterns_user = [
    url(r'^login$',
        views.LoginView.as_view(template_name='user/login.html',
                                authentication_form=UserLoginForm),
        name='login'),
    url(r'^logout$',
        user.logout,
        name='logout'),
    url(r'^delete$',
        user.delete,
        name='delete'),
    url(r'^(?P<user_pk>\d+)/delete$',
        user.delete,
        name='delete'),
    url(r'^(?P<user_pk>\d+)/trainer-login$',
        user.trainer_login,
        name='trainer-login'),
    url(r'^registration$',
        user.registration,
        name='registration'),
    url(r'^preferences$',
        user.preferences,
        name='preferences'),
    url(r'^api-key$',
        user.api_key,
        name='api-key'),
    url(r'^demo-entries$',
        misc.demo_entries,
        name='demo-entries'),
    url(r'^(?P<pk>\d+)/activate',
        user.UserActivateView.as_view(),
        name='activate'),
    url(r'^(?P<pk>\d+)/deactivate',
        user.UserDeactivateView.as_view(),
        name='deactivate'),
    url(r'^(?P<pk>\d+)/edit',
        user.UserEditView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/overview',
        user.UserDetailView.as_view(),
        name='overview'),
    url(r'^list',
        user.UserListView.as_view(),
        name='list'),

    # Password reset is implemented by Django, no need to cook our own soup here
    # (besides the templates)
    url(r'^password/change$',
        views.PasswordChangeView.as_view(success_url=reverse_lazy('core:user:preferences')),
        {'template_name': 'user/change_password.html',
         'post_change_redirect': reverse_lazy('core:user:preferences')},
        name='change-password'),
    url(r'^password/reset/$',
        views.PasswordResetView.as_view(),
        {'template_name': 'user/password_reset_form.html',
         'email_template_name': 'user/password_reset_email.html',
         'post_reset_redirect': reverse_lazy('core:user:password_reset_done')},
        name='password_reset'),
    url(r'^password/reset/done/$',
        views.PasswordResetDoneView.as_view(),
        {'template_name': 'user/password_reset_done.html'},
        name='password_reset_done'),
    url(r'^password/reset/check/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        views.PasswordResetConfirmView.as_view(),
        {'template_name': 'user/password_reset_confirm.html',
         'post_reset_redirect': reverse_lazy('core:user:password_reset_complete')},
        name='password_reset_confirm'),
    url(r'^password/reset/complete/$',
        views.PasswordResetCompleteView.as_view(),
        {'template_name': 'user/password_reset_complete.html'},
        name='password_reset_complete'),
]


# sub patterns for licenses
patterns_license = [
    url(r'^license/list$',
        license.LicenseListView.as_view(),
        name='list'),
    url(r'^license/add$',
        license.LicenseAddView.as_view(),
        name='add'),
    url(r'^license/(?P<pk>\d+)/edit',
        license.LicenseUpdateView.as_view(),
        name='edit'),
    url(r'^license/(?P<pk>\d+)/delete',
        license.LicenseDeleteView.as_view(),
        name='delete'),
]

# sub patterns for setting units
patterns_repetition_units = [
    url(r'^list$',
        repetition_units.ListView.as_view(),
        name='list'),
    url(r'^add$',
        repetition_units.AddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit',
        repetition_units.UpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete',
        repetition_units.DeleteView.as_view(),
        name='delete'),
]

# sub patterns for setting units
patterns_weight_units = [
    url(r'^list$',
        weight_units.ListView.as_view(),
        name='list'),
    url(r'^add$',
        weight_units.AddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit',
        weight_units.UpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete',
        weight_units.DeleteView.as_view(),
        name='delete'),
]


#
# Actual patterns
#
urlpatterns = [

    # The landing page
    url(r'^$',
        misc.index,
        name='index'),

    # The dashboard
    url(r'^dashboard$',
        misc.dashboard,
        name='dashboard'),

    # Others
    url(r'^about$',
        TemplateView.as_view(template_name="misc/about.html"),
        name='about'),
    url(r'^contact$',
        misc.ContactClassView.as_view(template_name="misc/contact.html"),
        name='contact'),
    url(r'^feedback$',
        misc.FeedbackClass.as_view(),
        name='feedback'),

    url(r'^language/', include((patterns_language, 'language'), namespace="language")),
    url(r'^user/', include((patterns_user, 'user'), namespace="user")),
    url(r'^license/', include((patterns_license, 'license'), namespace="license")),
    url(r'^repetition-unit/', include((patterns_repetition_units, 'repetition-unit'), namespace="repetition-unit")),
    url(r'^weight-unit/', include((patterns_weight_units, 'weight-unit'), namespace="weight-unit")),
]
