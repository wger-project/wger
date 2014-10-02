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


from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from django.contrib.auth import views
from django.core.urlresolvers import reverse_lazy

from wger.core.views import user
from wger.core.views import misc
from wger.core.views import license
from wger.core.views import gym

# Gyms
patterns_gym = patterns('',
    url(r'^list$',
        gym.GymListView.as_view(),
        name='list'),
    url(r'^new-user-data/view$',
        gym.gym_new_user_info,
        name='new-user-data'),
    url(r'^new-user-data/export$',
        gym.gym_new_user_info_export,
        name='new-user-data-export'),
    url(r'^(?P<pk>\d+)/members',
        gym.GymUserListView.as_view(),
        name='user-list'),
    url(r'^(?P<gym_pk>\d+)/add-member',
        gym.GymAddUserView.as_view(),
        name='add-user'),
    url(r'^add$',
        gym.GymAddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit',
        gym.GymUpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete',
        gym.GymDeleteView.as_view(),
        name='delete'),
)

urlpatterns = patterns('',

    # The landing page
    url(r'^$',
        misc.index,
        name='index'),

    # The dashboard
    url(r'^dashboard$',
        misc.dashboard,
        name='dashboard'),

    # User
    url(r'^user/delete$',
        user.delete,
        name='user-delete'),
    url(r'^user/(?P<user_pk>\d+)/delete$',
        user.delete,
        name='user-delete'),
    url(r'^user/logout$',
        user.logout,
        name='logout'),
    url(r'^user/(?P<user_pk>\d+)/trainer-login$',
        user.trainer_login,
        name='trainer-login'),
    url(r'^user/registration$',
        user.registration,
        name='registration'),
    url(r'^user/preferences$',
        user.preferences,
        name='preferences'),
    url(r'^user/api-key$',
        user.api_key,
        name='api-key'),
    url(r'^user/demo-entries$',
        misc.demo_entries,
        name='demo-entries'),
    url(r'^user/(?P<pk>\d+)/activate',
        user.UserActivateView.as_view(),
        name='user-activate'),
    url(r'^user/(?P<pk>\d+)/deactivate',
        user.UserDeactivateView.as_view(),
        name='user-deactivate'),
    url(r'^user/(?P<pk>\d+)/edit',
        user.UserEditView.as_view(),
        name='user-edit'),
    url(r'^user/(?P<pk>\d+)/overview',
        user.UserDetailView.as_view(),
        name='user-overview'),

    # Licenses
    url(r'^license/list$',
        license.LicenseListView.as_view(),
        name='license-list'),
    url(r'^license/add$',
        license.LicenseAddView.as_view(),
        name='license-add'),
    url(r'^license/(?P<pk>\d+)/edit',
        license.LicenseUpdateView.as_view(),
        name='license-edit'),
    url(r'^license/(?P<pk>\d+)/delete',
        license.LicenseDeleteView.as_view(),
        name='license-delete'),
    
    url(r'^gym/', include(patterns_gym, namespace="gym")),

    

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
)

# Password reset is implemented by Django, no need to cook our own soup here
# (besides the templates)
urlpatterns = urlpatterns + patterns('',
    url(r'^user/login$',
        user.login,
        name='login'),

    url(r'^user/password/change$',
        views.password_change,
        {'template_name': 'user/change_password.html',
          'post_change_redirect': reverse_lazy('core:preferences')},
        name='change-password'),

    url(r'^user/password/reset/$',
        views.password_reset,
        {'template_name': 'user/password_reset_form.html',
         'email_template_name': 'user/password_reset_email.html',
         'post_reset_redirect': reverse_lazy('core:password_reset_done')},
        name='password_reset'),

    url(r'^user/password/reset/done/$',
        views.password_reset_done,
        {'template_name': 'user/password_reset_done.html'},
        name='password_reset_done'),

    url(r'^user/password/reset/check/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        views.password_reset_confirm,
        {'template_name': 'user/password_reset_confirm.html',
         'post_reset_redirect': reverse_lazy('core:password_reset_complete')},
        name='password_reset_confirm'),

    url(r'^user/password/reset/complete/$',
        views.password_reset_complete,
        {'template_name': 'user/password_reset_complete.html'},
        name='password_reset_complete'),
)
