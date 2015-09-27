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


from django.conf.urls import (
    patterns,
    url,
    include
)
from django.views.generic import TemplateView
from django.contrib.auth import views
from django.core.urlresolvers import reverse_lazy

from wger.core.views import (
    user,
    misc,
    license
)

# sub patterns for languages
patterns_user = [
    url(r'^login$',
        user.login,
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

    # Password reset is implemented by Django, no need to cook our own soup here
    # (besides the templates)
    url(r'^password/change$',
        views.password_change,
        {'template_name': 'user/change_password.html',
          'post_change_redirect': reverse_lazy('core:user:preferences')},
        name='change-password'),
    url(r'^password/reset/$',
        views.password_reset,
        {'template_name': 'user/password_reset_form.html',
         'email_template_name': 'user/password_reset_email.html',
         'post_reset_redirect': reverse_lazy('core:user:password_reset_done')},
        name='password_reset'),
    url(r'^password/reset/done/$',
        views.password_reset_done,
        {'template_name': 'user/password_reset_done.html'},
        name='password_reset_done'),
    url(r'^password/reset/check/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        views.password_reset_confirm,
        {'template_name': 'user/password_reset_confirm.html',
         'post_reset_redirect': reverse_lazy('core:user:password_reset_complete')},
        name='password_reset_confirm'),
    url(r'^password/reset/complete/$',
        views.password_reset_complete,
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

    url(r'^user/', include(patterns_user, namespace="user")),
    url(r'^license/', include(patterns_license, namespace="license")),
]
