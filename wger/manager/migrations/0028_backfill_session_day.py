from django.core.cache import cache
from django.db import (
    migrations,
    models,
    transaction,
)

from wger.utils.cache import CacheKeyMapper


BATCH_SIZE = 2000


def clear_routine_caches(routines):
    """
    Drops the cached date sequences of the given (routine, user) pairs.

    The sequence is cached for a month, so without this the routines would keep
    serving the stalled sequence the backfill just repaired. The structure is
    untouched and keeps its cache.
    """
    keys = []
    for routine_id, user_id in routines:
        keys.append(CacheKeyMapper.routine_date_sequence_key(routine_id))
        keys.append(CacheKeyMapper.routine_api_date_sequence_display_key(routine_id, user_id))
        keys.append(CacheKeyMapper.routine_api_date_sequence_gym_key(routine_id, user_id))
        keys.append(CacheKeyMapper.routine_api_logs(routine_id, user_id))
        keys.append(CacheKeyMapper.routine_api_stats(routine_id, user_id))

    for i in range(0, len(keys), BATCH_SIZE):
        cache.delete_many(keys[i : i + BATCH_SIZE])


def backfill_session_day(apps, schema_editor):
    """
    Set the day on sessions that were created automatically for a log.

    Until recently these were created with only a user, date and routine, which
    made them invisible to days with need_logs_to_advance: that gate looks
    sessions up by their day. The affected routines stall on the gated day
    since it can't advance.

    The day is recovered from the session's logs, which point at a slot entry
    and through it at the day. Sessions whose logs span several days, or that
    have no logs on a routine day at all, are left alone: a wrong day would
    open the gate on a day the user never trained.
    """
    WorkoutSession = apps.get_model('manager', 'WorkoutSession')
    WorkoutLog = apps.get_model('manager', 'WorkoutLog')

    resolved = (
        WorkoutLog.objects.filter(
            session__day__isnull=True,
            session__routine__isnull=False,
            slot_entry__isnull=False,
            # Only trust logs whose day actually belongs to the session's routine
            slot_entry__slot__day__routine=models.F('session__routine'),
        )
        .values('session_id')
        .annotate(
            day_count=models.Count('slot_entry__slot__day', distinct=True),
            day_id=models.Min('slot_entry__slot__day'),
        )
        .filter(day_count=1)
        .values_list('session_id', 'day_id', 'session__routine_id', 'session__user_id')
        .order_by('session_id')
        .iterator()
    )

    batch = []
    touched_routines = set()

    for session_id, day_id, routine_id, user_id in resolved:
        batch.append(WorkoutSession(pk=session_id, day_id=day_id))
        touched_routines.add((routine_id, user_id))

        if len(batch) >= BATCH_SIZE:
            WorkoutSession.objects.bulk_update(batch, ['day_id'])
            batch = []

    if batch:
        WorkoutSession.objects.bulk_update(batch, ['day_id'])

    # Only after the commit: while the transaction is open, a concurrent read
    # still sees the old rows and would cache the stalled sequence again
    if touched_routines:
        transaction.on_commit(lambda: clear_routine_caches(touched_routines))


class Migration(migrations.Migration):
    dependencies = [
        ('manager', '0027_cleanup_fields'),
    ]

    operations = [
        migrations.RunPython(backfill_session_day, migrations.RunPython.noop),
    ]
