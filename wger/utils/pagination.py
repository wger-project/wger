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

# Third Party
from rest_framework.pagination import CursorPagination


class IngredientCursorPagination(CursorPagination):
    """
    Cursor-based pagination for ingredient sync.

    Unlike the default LimitOffsetPagination, cursor pagination performs in
    O(log n) per page regardless of how deep the client is paginating, because
    it uses the B-tree index on the primary key directly instead of sorting and
    skipping rows.

    Trade-offs (compared to LimitOffsetPagination):
        - No total `count` in the response (would require a separate query)
        - No random access (clients can only follow `next`/`previous`)
        - Ordering must be a unique, monotonic field (we use `id`)

    Designed for sync clients (mobile apps, federated wger instances) that
    iterate through the catalogue once. UI list views with pagers should keep
    using LimitOffsetPagination.
    """

    page_size = 200
    max_page_size = 1000
    page_size_query_param = 'page_size'
    ordering = 'id'
    cursor_query_param = 'cursor'
