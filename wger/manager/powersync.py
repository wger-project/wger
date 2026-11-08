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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# wger
from wger.manager.api.serializers import (
    RoutineSerializer,
    WorkoutLogSerializer,
    WorkoutSessionSerializer,
)
from wger.manager.api.views import (
    RoutineViewSet,
    WorkoutLogViewSet,
    WorkoutSessionViewSet,
)
from wger.manager.models import (
    Routine,
    WorkoutLog,
    WorkoutSession,
)
from wger.utils.powersync import (
    PowerSyncHandler,
    register_handler,
)


@register_handler
class WorkoutLogHandler(PowerSyncHandler):
    """
    Logs reference both a ``Routine`` and a ``WorkoutSession``; the serializer
    consults ``user_id`` from the context when pinning a log to a session.
    """

    model = WorkoutLog
    serializer_class = WorkoutLogSerializer
    viewset_class = WorkoutLogViewSet
    pass_user_id_in_context = True


@register_handler
class WorkoutSessionHandler(PowerSyncHandler):
    model = WorkoutSession
    serializer_class = WorkoutSessionSerializer
    viewset_class = WorkoutSessionViewSet


@register_handler
class RoutineHandler(PowerSyncHandler):
    """
    Creation goes through REST so the backend can assign the integer PK and
    ``created`` timestamp; only PATCH/DELETE arrive via PowerSync.
    """

    model = Routine
    serializer_class = RoutineSerializer
    viewset_class = RoutineViewSet
    supports_create = False
