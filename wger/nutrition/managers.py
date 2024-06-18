#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) wger Team
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Django
from django.conf import settings
from django.db import connections
from django.db.models import (
    Manager,
    QuerySet,
)

# wger
from wger.utils.db import is_postgres_db


class ApproximateCountQuerySet(QuerySet):
    """
    Approximate count query set, postgreSQL only

    While this doesn't return an exact count, it does return an approximate
    in a much shorter amount of time, which is specially important for the
    ingredients

    https://testdriven.io/blog/django-approximate-counting/
    """

    def count(self):
        if self.query.where:
            return super(ApproximateCountQuerySet, self).count()

        if is_postgres_db() and not settings.TESTING:
            cursor = connections[self.db].cursor()
            cursor.execute(
                "SELECT reltuples FROM pg_class WHERE relname = '%s';" % self.model._meta.db_table
            )

            return int(cursor.fetchone()[0])

        return super(ApproximateCountQuerySet, self).count()


ApproximateCountManager = Manager.from_queryset(ApproximateCountQuerySet)
