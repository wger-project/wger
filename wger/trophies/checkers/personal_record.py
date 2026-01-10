#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2021 wger Team
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

# Standard Library
import logging
from decimal import Decimal
from typing import Optional

# wger
from wger.manager.models import WorkoutLog
from wger.trophies.models.trophy import Trophy
from wger.trophies.models.user_trophy import UserTrophy

# Local
from .base import BaseTrophyChecker


logger = logging.getLogger(__name__)


class PersonalRecordChecker(BaseTrophyChecker):
    """
    Checker for Personal Record (PR) repeatable trophy.

    Used to detect when PRs are beaten and award trophies accordingly.

    params:
        log (WorkoutLog): workout log used to check if a PR was beaten.

    """

    def _estimate_one_rep_max(self) -> float:
        """
        Estimates the user's one-rep max (1RM) using Brzycki's formula:
        1RM = weight * (36 / (37 - repetitions))

        Note: returning float because of serialization issues with Decimal in JSON.
        """
        log: WorkoutLog | None = self.params.get('log')
        if not log:
            raise ValueError('Log should not be None')

        weight = log.weight
        repetitions = log.repetitions
        rir = log.rir

        if weight is None:
            raise ValueError('Weight should not be None')
        if repetitions is None:
            raise ValueError('Repetitions should not be None')
        if rir is not None:
            repetitions += rir

        if repetitions == 37:
            raise ValueError("In Brzycki's formula, repetitions cannot be equal to 37.")

        result = weight * (Decimal('36') / (Decimal('37') - repetitions))
        return round(float(result), 2)

    def check(self) -> bool:
        """Check if user has beaten Personal Record."""
        log = self.params.get('log', None)

        if not log:
            return False

        exercise = getattr(log, 'exercise', None)

        pr_trophy = Trophy.objects.get(name='Personal Record')
        if not pr_trophy:
            raise Exception("Trophy 'Personal Record' not found.")

        last_pr = (
            UserTrophy.objects.filter(
                user=log.user,
                trophy=pr_trophy,
                context_data__exercise_id=exercise.id,
            )
            .order_by('-earned_at')
            .first()
        )

        if last_pr and last_pr.context_data:
            prev = last_pr.context_data.get('one_rep_max_estimate')
            try:
                current = self._estimate_one_rep_max()
            except Exception:
                return False

            if prev is not None and prev >= current:
                return False

        return True

    def get_progress(self) -> float:
        """Get progress as percentage."""
        return 100.0 if self.check() else 0.0

    def get_context_data(self) -> Optional[dict]:
        log: WorkoutLog | None = self.params.get('log', None)

        if not log:
            return None

        session = log.session
        exercise = log.exercise
        repetitions_unit = log.repetitions_unit
        weight_unit = log.weight_unit
        repetitions = log.repetitions
        weight = log.weight

        try:
            one_rm_estimate = self._estimate_one_rep_max()
        except Exception as e:
            logger.warning(f'PR estimation failed : {e}')
            one_rm_estimate = None

        return {
            'log_id': log.id,
            'date': log.date.isoformat(),
            'session_id': session.id if session else None,
            'exercise_id': exercise.id if exercise else None,
            'repetitions_unit_id': repetitions_unit.id if repetitions_unit else None,
            'repetitions': float(repetitions) if repetitions else None,
            'weight_unit_id': weight_unit.id if weight_unit else None,
            'weight': float(weight) if weight else None,
            'iteration': log.iteration,
            'one_rep_max_estimate': one_rm_estimate,
        }

    def get_target_value(self) -> str:
        return 'N/A'

    def get_current_value(self) -> str:
        return 'N/A'

    def get_progress_display(self) -> str:
        return 'N/A'
