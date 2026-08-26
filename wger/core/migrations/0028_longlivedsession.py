from django.conf import settings
from django.contrib.sessions.backends.db import SessionStore
from django.db import migrations, models
from django.utils import timezone
from django.utils.dateparse import parse_datetime

import django.db.models.deletion


"""
Indexes the long-lived sessions of the headless refresh tokens.

The session table has no user column, so the overview at /user/api-key used to
decode every unexpired session of the whole instance to find the ones of the
logged-in user. New sessions are indexed when they are minted, the ones that
already exist are collected here once.
"""

# The one place where the whole table has to be read. Sessions are loaded in
# chunks and without the columns nobody needs to keep the memory flat.
CHUNK_SIZE = 2000

# Copies of the keys in wger.utils.headless_long_lived, a migration has to keep
# working when those change.
SESSION_KEY = '_auth_user_id'
LONG_LIVED_FLAG = 'wger_long_lived_refresh'
LONG_LIVED_CREATED_AT = 'wger_long_lived_refresh_created_at'


def index_existing_sessions(session_model, index_model, user_model):
    """
    Create an index row for every unexpired long-lived session
    """
    store = SessionStore()
    now = timezone.now()
    found = []

    queryset = session_model.objects.filter(expire_date__gt=now).only(
        'session_key',
        'session_data',
    )
    for session in queryset.iterator(chunk_size=CHUNK_SIZE):
        try:
            data = store.decode(session.session_data)
        except Exception:
            continue

        if not data.get(LONG_LIVED_FLAG) or not data.get(SESSION_KEY):
            continue

        found.append(
            (
                data[SESSION_KEY],
                session.session_key,
                parse_datetime(data.get(LONG_LIVED_CREATED_AT) or '') or now,
            )
        )

    # Sessions of users that were deleted in the meantime would violate the
    # foreign key.
    known = {
        str(pk)
        for pk in user_model.objects.filter(pk__in={row[0] for row in found}).values_list(
            'pk', flat=True
        )
    }
    index_model.objects.bulk_create(
        [
            index_model(
                user_id=user_id,
                session_key=session_key,
                created=created,
            )
            for user_id, session_key, created in found
            if user_id in known
        ],
        ignore_conflicts=True,
        batch_size=CHUNK_SIZE,
    )


def forwards(apps, schema_editor):
    index_existing_sessions(
        apps.get_model('sessions', 'Session'),
        apps.get_model('core', 'LongLivedSession'),
        apps.get_model(settings.AUTH_USER_MODEL),
    )


class Migration(migrations.Migration):
    dependencies = [
        ('sessions', '0001_initial'),
        ('core', '0027_powersync_publication'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LongLivedSession',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name='ID'
                    ),
                ),
                ('session_key', models.CharField(editable=False, max_length=40, unique=True)),
                ('created', models.DateTimeField(default=timezone.now, editable=False)),
                (
                    'user',
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='long_lived_sessions',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.RunPython(forwards, migrations.RunPython.noop, elidable=True),
    ]
