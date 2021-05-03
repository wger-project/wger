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
from django.urls import path

# wger
from wger.gym.views import (
    admin_config,
    admin_notes,
    config,
    contract,
    contract_option,
    contract_type,
    document,
    export,
    gym,
    user_config
)


# 'sub patterns' for gyms
patterns_gym = [
    path('list',
         gym.GymListView.as_view(),
         name='list'),
    path('new-user-data/view',
         gym.gym_new_user_info,
         name='new-user-data'),
    path('new-user-data/export',
         gym.gym_new_user_info_export,
         name='new-user-data-export'),
    path('<int:pk>/members',
         gym.GymUserListView.as_view(),
         name='user-list'),
    path('<int:gym_pk>/add-member',
         gym.GymAddUserView.as_view(),
         name='add-user'),
    path('add',
         gym.GymAddView.as_view(),
         name='add'),
    path('<int:pk>/edit',
         gym.GymUpdateView.as_view(),
         name='edit'),
    path('<int:pk>/delete',
         gym.GymDeleteView.as_view(),
         name='delete'),
    path('user/<int:user_pk>/permission-edit',
         gym.gym_permissions_user_edit,
         name='edit-user-permission'),
    path('user/<int:user_pk>/reset-user-password',
         gym.reset_user_password,
         name='reset-user-password'),
]

# 'sub patterns' for gym config
patterns_gymconfig = [
    path('<int:pk>/edit',
         config.GymConfigUpdateView.as_view(),
         name='edit'),
]


# 'sub patterns' for gym admin config
patterns_adminconfig = [
    path('<int:pk>/edit',
         admin_config.ConfigUpdateView.as_view(),
         name='edit'),
]

# 'sub patterns' for gym user config
patterns_userconfig = [
    path('<int:pk>/edit',
         user_config.ConfigUpdateView.as_view(),
         name='edit'),
]

# 'sub patterns' for admin notes
patterns_admin_notes = [
    path('list/user/<int:user_pk>',
         admin_notes.ListView.as_view(),
         name='list'),
    path('add/user/<int:user_pk>',
         admin_notes.AddView.as_view(),
         name='add'),
    path('<int:pk>/edit',
         admin_notes.UpdateView.as_view(),
         name='edit'),
    path('<int:pk>/delete',
         admin_notes.DeleteView.as_view(),
         name='delete'),
]

# 'sub patterns' for user documents
patterns_documents = [
    path('list/user/<int:user_pk>',
         document.ListView.as_view(),
         name='list'),
    path('add/user/<int:user_pk>',
         document.AddView.as_view(),
         name='add'),
    path('<int:pk>/edit',
         document.UpdateView.as_view(),
         name='edit'),
    path('<int:pk>/delete',
         document.DeleteView.as_view(),
         name='delete'),
]

# sub patterns for contracts
patterns_contracts = [
    path('add/<int:user_pk>',
         contract.AddView.as_view(),
         name='add'),
    path('view/<int:pk>',
         contract.DetailView.as_view(),
         name='view'),
    path('edit/<int:pk>',
         contract.UpdateView.as_view(),
         name='edit'),
    path('list/<int:user_pk>',
         contract.ListView.as_view(),
         name='list'),
]

# sub patterns for contract types
patterns_contract_types = [
    path('add/<int:gym_pk>',
         contract_type.AddView.as_view(),
         name='add'),
    path('edit/<int:pk>',
         contract_type.UpdateView.as_view(),
         name='edit'),
    path('delete/<int:pk>',
         contract_type.DeleteView.as_view(),
         name='delete'),
    path('list/<int:gym_pk>',
         contract_type.ListView.as_view(),
         name='list'),
]

# sub patterns for contract options
patterns_contract_options = [
    path('add/<int:gym_pk>',
         contract_option.AddView.as_view(),
         name='add'),
    path('edit/<int:pk>',
         contract_option.UpdateView.as_view(),
         name='edit'),
    path('delete/<int:pk>',
         contract_option.DeleteView.as_view(),
         name='delete'),
    path('list/<int:gym_pk>',
         contract_option.ListView.as_view(),
         name='list'),
]

# sub patterns for exports
patterns_export = [
    path('users/<int:gym_pk>)',
         export.users,
         name='users'),
]

#
# All patterns for this app
#
urlpatterns = [
    path('', include((patterns_gym, 'gym'), namespace="gym")),
    path('config/', include((patterns_gymconfig, 'config'), namespace="config")),
    path('admin-config/', include((patterns_adminconfig, 'admin_config'), namespace="admin_config")),
    path('user-config/', include((patterns_userconfig, 'user_config'), namespace="user_config")),
    path('notes/', include((patterns_admin_notes, 'admin_note'), namespace="admin_note")),
    path('document/', include((patterns_documents, 'document'), namespace="document")),
    path('contract/', include((patterns_contracts, 'contract'), namespace="contract")),
    path('contract-type/', include((patterns_contract_types, 'contract_type'), namespace="contract_type")),
    path('contract-option/', include((patterns_contract_options, 'contract-option'), namespace="contract-option")),
    path('export/', include((patterns_export, 'export'), namespace="export")),
]
