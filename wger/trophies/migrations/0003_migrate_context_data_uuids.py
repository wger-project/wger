# Generated manually for PowerSync UUID PK migration.

from django.db import migrations
from django.db.migrations.state import StateApps


def migrate_context_data_uuids(apps: StateApps, schema_editor):
    """
    Migrate the int PKs of Log and Session objects to UUIDs (strings)
    """
    UserTrophy = apps.get_model('trophies', 'UserTrophy')
    WorkoutLog = apps.get_model('manager', 'WorkoutLog')
    WorkoutSession = apps.get_model('manager', 'WorkoutSession')

    log_uuid_cache = {}
    session_uuid_cache = {}

    def resolve(cache: dict, model, old_id: int):
        if old_id not in cache:
            cache[old_id] = model.objects.filter(id=old_id).values_list('uuid', flat=True).first()
        return cache[old_id]

    for user_trophy in  UserTrophy.objects.exclude(context_data__isnull=True).iterator():
        context = user_trophy.context_data
        if not isinstance(context, dict):
            continue

        changed = False

        log_id = context.get('log_id')
        if isinstance(log_id, int):
            uuid = resolve(log_uuid_cache, WorkoutLog, log_id)
            if uuid is not None:
                context['log_id'] = str(uuid)
                changed = True

        session_id = context.get('session_id')
        if isinstance(session_id, int):
            uuid = resolve(session_uuid_cache, WorkoutSession, session_id)
            if uuid is not None:
                context['session_id'] = str(uuid)
                changed = True

        if changed:
            user_trophy.context_data = context
            user_trophy.save(update_fields=['context_data'])


class Migration(migrations.Migration):
    dependencies = [
        ('trophies', '0002_load_initial_trophies'),
        ('manager', '0025_change_pk_to_uuid'),
    ]

    run_before = [
        ('manager', '0026_change_pk_to_uuid_swap'),
    ]

    operations = [
        migrations.RunPython(
            migrate_context_data_uuids,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
