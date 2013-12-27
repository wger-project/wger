from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView

from wger.manager.views import schedule
from wger.manager.views import schedule_step
from wger.manager.views.workout import WorkoutEditView
from wger.manager.views.workout import WorkoutDeleteView
from wger.manager.views.log import WorkoutLogDetailView
from wger.manager.views.log import WorkoutLogAddView
from wger.manager.views.log import WorkoutLogUpdateView
from wger.manager.views.day import DayEditView
from wger.manager.views.day import DayCreateView
from wger.manager.views import misc
from wger.manager.views import ical
from wger.manager.views import user

from wger.utils.constants import USER_TAB


urlpatterns = patterns('wger.manager.views',

    # The landing page
    url(r'^$',
        'misc.index',
        name='index'),

    # The dashboard
    url(r'^dashboard$',
        'misc.dashboard',
        name='dashboard'),

    # User
    url(r'^user/logout$',
        'user.logout',
        name='logout'),
    url(r'^user/registration$',
        'user.registration',
        name='registration'),
    url(r'^user/preferences$',
        'user.preferences',
        name='preferences'),
    url(r'^user/demo-entries$',
        'misc.demo_entries',
        name='demo-entries'),
    url(r'^user/api-key$',
        'user.api_key',
        name='api-key'),

    # Workout
    url(r'^workout/overview$',
        'workout.overview',
        name='workout-overview'),
    url(r'^workout/add$',
        'workout.add',
        name='workout-add'),
    url(r'^workout/(?P<pk>\d+)/copy/$',
        'workout.copy_workout',
        name='workout-copy'),
    url(r'^workout/(?P<pk>\d+)/edit/$',
        WorkoutEditView.as_view(),
        name='workout-edit'),
    url(r'^workout/(?P<pk>\d+)/delete/$',
        WorkoutDeleteView.as_view(),
        name='workout-delete'),
    url(r'^workout/(?P<id>\d+)/view/$',
        'workout.view',
        name='workout-view'),
    url(r'^workout/(?P<pk>\d+)/log/$',
        WorkoutLogDetailView.as_view(),
        name='workout-log'),
    url(r'^workout/log/edit-entry/(?P<pk>\d+)$',
        WorkoutLogUpdateView.as_view(),
        name='workout-log-edit'),
    url(r'^workout/(?P<workout_pk>\d+)/log/add$',
        WorkoutLogAddView.as_view(),
        name='workout-log-add'),
    url(r'^workout/calendar$',
        'log.calendar',
        name='workout-calendar'),
    url(r'^workout/calendar/(?P<year>\d{4})-(?P<month>\d{1,2})$',
        'log.calendar',
        name='workout-calendar'),
    url(r'^workout/(?P<pk>\d+)/ical$',
        ical.export,
        name='workout-ical'),

    # Timer
    url(r'^workout/(?P<pk>\d+)/timer$',
        'workout.timer',
        name='workout-timer'),

    # Schedules
    url(r'^workout/schedule/overview$',
        'schedule.overview',
        name='schedule-overview'),
    url(r'^workout/schedule/add$',
        schedule.ScheduleCreateView.as_view(),
        name='schedule-add'),
    url(r'^workout/schedule/(?P<pk>\d+)/view/$',
        'schedule.view',
        name='schedule-view'),
    url(r'^workout/schedule/(?P<pk>\d+)/edit/$',
        schedule.ScheduleEditView.as_view(),
        name='schedule-edit'),
    url(r'^workout/schedule/(?P<pk>\d+)/delete/$',
        schedule.ScheduleDeleteView.as_view(),
        name='schedule-delete'),
    url(r'^workout/schedule/(?P<pk>\d+)/ical$',
        ical.export_schedule,
        name='schedule-ical'),
    url(r'^workout/schedule/api/(?P<pk>\d+)/edit$',
        'schedule.edit_step_api',
        name='schedule-edit-api'),

    # Schedule steps
    url(r'^workout/schedule/(?P<schedule_pk>\d+)/step/add$',
        schedule_step.StepCreateView.as_view(),
        name='step-add'),
    url(r'^workout/schedule/step/(?P<pk>\d+)/edit$',
        schedule_step.StepEditView.as_view(),
        name='step-edit'),
    url(r'^workout/schedule/step/(?P<pk>\d+)/delete$',
        schedule_step.StepDeleteView.as_view(),
        name='step-delete'),

    # Days
    url(r'^workout/day/(?P<pk>\d+)/edit/$',
        login_required(DayEditView.as_view()),
        name='day-edit'),
    url(r'^workout/(?P<workout_pk>\d+)/day/add/$',
        login_required(DayCreateView.as_view()),
        name='day-add'),
    url(r'^workout/(?P<id>\d+)/day/(?P<day_id>\d+)/delete/$', 'day.delete'),
    url(r'^workout/day/(?P<id>\d+)/view/$', 'day.view'),
    url(r'^workout/day/(?P<pk>\d+)/log/add/$',
        'log.add',
        name='day-log'),

    # Sets and Settings
    url(r'^workout/day/(?P<day_pk>\d+)/set/add/$',
        'set.create',
        name='set-add'),
    url(r'^workout/get-formset/(?P<exercise_pk>\d+)/(?P<reps>\d+)/',
        'set.get_formset',
        name='set-get-formset'),  # Used by JS
    url(r'^workout/set/(?P<pk>\d+)/delete$', 'set.delete'),
    url(r'^workout/set/(?P<pk>\d+)/edit/$',
        'set.edit',
        name='set-edit'),

    # AJAX
    url(r'^workout/api/edit-set$', 'set.api_edit_set'),
    url(r'^workout/api/user-preferences$', 'user.api_user_preferences'),

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

# PDF stuff is in a different file
urlpatterns = urlpatterns + patterns('wger.manager.pdf',
     url(r'^workout/(?P<id>\d+)/pdf/$', 'workout_log'))

# Password reset is implemented by Django, no need to cook our own soup here
# (besides the templates)
urlpatterns = urlpatterns + patterns('',
    url(r'^user/login$',
        user.login,
        name='login'),

    url(r'^user/password/change$',
        'django.contrib.auth.views.password_change',
        {'template_name': 'user/change_password.html',
          'post_change_redirect': reverse_lazy('preferences'),
          'extra_context': {'active_tab': USER_TAB}},
        name='change-password'),

    url(r'^user/password/reset/$',
        'django.contrib.auth.views.password_reset',
        {'template_name': 'user/password_reset_form.html'},
        name='password_reset'),

    url(r'^user/password/reset/done/$',
        'django.contrib.auth.views.password_reset_done',
        {'template_name': 'user/password_reset_done.html'},
        name='password_reset_done'),

    url(r'^user/password/reset/check/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        'django.contrib.auth.views.password_reset_confirm',
        {'template_name': 'user/password_reset_confirm.html'},
        name='password_reset_confirm'),

    url(r'^user/password/reset/complete/$',
        'django.contrib.auth.views.password_reset_complete',
        {'template_name': 'user/password_reset_complete.html'},
        name='password_reset_complete'),
    )
