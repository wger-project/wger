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
    url,
    include
)

from wger.gym.views import (
    gym,
    config,
    admin_config,
    user_config,
    admin_notes,
    document,
    contract,
    contract_type,
    contract_option,
    export
)


# 'sub patterns' for gyms
patterns_gym = [
    url(r'^list$',
        gym.GymListView.as_view(),
        name='list'),
    url(r'^new-user-data/view$',
        gym.gym_new_user_info,
        name='new-user-data'),
    url(r'^new-user-data/export$',
        gym.gym_new_user_info_export,
        name='new-user-data-export'),
    url(r'^(?P<pk>\d+)/members$',
        gym.GymUserListView.as_view(),
        name='user-list'),
    url(r'^(?P<gym_pk>\d+)/add-member$',
        gym.GymAddUserView.as_view(),
        name='add-user'),
    url(r'^add$',
        gym.GymAddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit$',
        gym.GymUpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete$',
        gym.GymDeleteView.as_view(),
        name='delete'),
    url(r'^user/(?P<user_pk>\d+)/permission-edit$',
        gym.gym_permissions_user_edit,
        name='edit-user-permission'),
    url(r'^user/(?P<user_pk>\d+)/reset-user-password$',
        gym.reset_user_password,
        name='reset-user-password'),
]

# 'sub patterns' for gym config
patterns_gymconfig = [
    url(r'^(?P<pk>\d+)/edit$',
        config.GymConfigUpdateView.as_view(),
        name='edit'),
]


# 'sub patterns' for gym admin config
patterns_adminconfig = [
    url(r'^(?P<pk>\d+)/edit$',
        admin_config.ConfigUpdateView.as_view(),
        name='edit'),
]

# 'sub patterns' for gym user config
patterns_userconfig = [
    url(r'^(?P<pk>\d+)/edit$',
        user_config.ConfigUpdateView.as_view(),
        name='edit'),
]

# 'sub patterns' for admin notes
patterns_admin_notes = [
    url(r'^list/user/(?P<user_pk>\d+)$',
        admin_notes.ListView.as_view(),
        name='list'),
    url(r'^add/user/(?P<user_pk>\d+)$',
        admin_notes.AddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit$',
        admin_notes.UpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete$',
        admin_notes.DeleteView.as_view(),
        name='delete'),
]

# 'sub patterns' for user documents
patterns_documents = [
    url(r'^list/user/(?P<user_pk>\d+)$',
        document.ListView.as_view(),
        name='list'),
    url(r'^add/user/(?P<user_pk>\d+)$',
        document.AddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit$',
        document.UpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete$',
        document.DeleteView.as_view(),
        name='delete'),
]

# sub patterns for contracts
patterns_contracts = [
    url(r'^add/(?P<user_pk>\d+)$',
        contract.AddView.as_view(),
        name='add'),
    url(r'^view/(?P<pk>\d+)$',
        contract.DetailView.as_view(),
        name='view'),
    url(r'^edit/(?P<pk>\d+)$',
        contract.UpdateView.as_view(),
        name='edit'),
    url(r'^list/(?P<user_pk>\d+)$',
        contract.ListView.as_view(),
        name='list'),
]

# sub patterns for contract types
patterns_contract_types = [
    url(r'^add/(?P<gym_pk>\d+)$',
        contract_type.AddView.as_view(),
        name='add'),
    url(r'^edit/(?P<pk>\d+)$',
        contract_type.UpdateView.as_view(),
        name='edit'),
    url(r'^delete/(?P<pk>\d+)$',
        contract_type.DeleteView.as_view(),
        name='delete'),
    url(r'^list/(?P<gym_pk>\d+)$',
        contract_type.ListView.as_view(),
        name='list'),
]

# sub patterns for contract options
patterns_contract_options = [
    url(r'^add/(?P<gym_pk>\d+)$',
        contract_option.AddView.as_view(),
        name='add'),
    url(r'^edit/(?P<pk>\d+)$',
        contract_option.UpdateView.as_view(),
        name='edit'),
    url(r'^delete/(?P<pk>\d+)$',
        contract_option.DeleteView.as_view(),
        name='delete'),
    url(r'^list/(?P<gym_pk>\d+)$',
        contract_option.ListView.as_view(),
        name='list'),
]

# sub patterns for exports
patterns_export = [
    url(r'^users/(?P<gym_pk>\d+)$',
        export.users,
        name='users'),
]

#
# All patterns for this app
#
urlpatterns = [
    url(r'^', include(patterns_gym, namespace="gym")),
    url(r'^config/', include(patterns_gymconfig, namespace="config")),
    url(r'^admin-config/', include(patterns_adminconfig, namespace="admin_config")),
    url(r'^user-config/', include(patterns_userconfig, namespace="user_config")),
    url(r'^notes/', include(patterns_admin_notes, namespace="admin_note")),
    url(r'^document/', include(patterns_documents, namespace="document")),
    url(r'^contract/', include(patterns_contracts, namespace="contract")),
    url(r'^contract-type/', include(patterns_contract_types, namespace="contract_type")),
    url(r'^contract-option/', include(patterns_contract_options, namespace="contract-option")),
    url(r'^export/', include(patterns_export, namespace="export")),
]
