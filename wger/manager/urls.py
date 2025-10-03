# -*- coding: utf-8 -*-
# Django
from django.urls import (
    include,
    path,
)

# wger
from wger.core.views.react import ReactView
from wger.manager.views import (
    ical,
    pdf,
    routine,
)


patterns_templates = [
    path('overview/private', ReactView.as_view(login_required=True), name='overview'),
    path('overview/public', ReactView.as_view(login_required=True), name='public'),
    path('<int:pk>/view', ReactView.as_view(login_required=True), name='view'),
]

patterns_days = [
    path('<int:day_pk>/add-logs', ReactView.as_view(), name='overview'),
]

patterns_routine = [
    path('overview', ReactView.as_view(login_required=True), name='overview'),
    path('add', ReactView.as_view(login_required=True), name='add'),
    path(
        '<int:pk>/edit',
        ReactView.as_view(login_required=True, div_id='react-page-no-shadow-dom'),
        name='edit',
    ),
    path(
        '<int:pk>/edit/progression/<int:progression_pk>',
        ReactView.as_view(login_required=True),
        name='edit-progression',
    ),
    path('<int:pk>/statistics', ReactView.as_view(login_required=True), name='statistics'),
    path('<int:pk>/logs', ReactView.as_view(login_required=True), name='logs'),
    path('<int:pk>/view', ReactView.as_view(login_required=True), name='view'),
    path('<int:pk>/table', ReactView.as_view(login_required=True), name='table'),
    path('<int:pk>/copy', routine.copy_routine, name='copy'),
    path('<int:pk>/pdf/log', pdf.workout_log, name='pdf-log'),
    path('<int:pk>/pdf/table', pdf.workout_view, name='pdf-table'),
    path('<int:pk>/ical', ical.export, name='ical'),
    path('calendar', ReactView.as_view(login_required=True), name='calendar'),
]

urlpatterns = [
    path('', include((patterns_routine, 'routine'), namespace='routine')),
    path('templates/', include((patterns_templates, 'template'), namespace='template')),
    path('<int:routine_pk>/day/', include((patterns_days, 'day'), namespace='day')),
]
