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

# Standard Library
import os

# Django
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

# Third Party
import environ


class Command(BaseCommand):
    """
    Bootstrap the PowerSync bucket storage in the wger Postgres database (itempotent).

    PowerSync needs its own dedicated user and schema inside the Postgres database
    to store its sync state. This command makes sure the database side matches by
    reading PS_STORAGE_PG_URI and creating/updating the role and schema.

    No-op if:

    * ``PS_STORAGE_PG_URI`` is unset (PowerSync not used).
    * The wger database isn't Postgres (PowerSync requires this backend).

    Safe to re-run on existing or fresh databases.
    """

    help = (
        'Idempotently bootstrap the PowerSync storage user and schema in '
        'the wger Postgres database. Reads connection details from '
        'PS_STORAGE_PG_URI. No-op if PowerSync is not configured.'
    )

    DEFAULT_SCHEMA = 'powersync'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema',
            default=self.DEFAULT_SCHEMA,
            help=f'Schema name to create (default: {self.DEFAULT_SCHEMA}).',
        )

    def handle(self, *args, **options):
        uri = os.environ.get('PS_STORAGE_PG_URI', '').strip()
        if not uri:
            self.stdout.write('PS_STORAGE_PG_URI not set — skipping PowerSync storage setup.')
            return

        if 'postgresql' not in settings.DATABASES['default']['ENGINE']:
            self.stdout.write(
                self.style.WARNING(
                    'wger database is not Postgres; PowerSync requires Postgres. Skipping.'
                )
            )
            return

        parsed = environ.Env.db_url_config(uri)
        target_user = parsed.get('USER')
        target_password = parsed.get('PASSWORD')
        target_db = parsed.get('NAME')
        if not (target_user and target_password and target_db):
            self.stdout.write(
                self.style.ERROR(
                    'PS_STORAGE_PG_URI must include user, password, and database name. '
                    'Skipping; fix the URI and re-run.'
                )
            )
            return

        # Sanity check: we can only bootstrap into the Postgres database that
        # Django itself is connected to. If the configuration differs and points
        # to a different one, the administrator needs to do the bootstrap there
        # manually.
        wger_db = settings.DATABASES['default']['NAME']
        if target_db != wger_db:
            self.stdout.write(
                self.style.ERROR(
                    f"PS_STORAGE_PG_URI targets database '{target_db}' but Django is "
                    f"connected to '{wger_db}'. Bootstrap that database manually: "
                    'https://docs.powersync.com/configuration/powersync-service/self-hosted-instances#postgres-storage'
                )
            )
            return

        schema = options['schema']

        # The DO-block below uses Postgres' `format()` with `%I` (identifier)
        # and `%L` (literal) escaping for fully safe interpolation server-side.
        # The `%%` are escaped percent signs that survive psycopg's own
        # `%s`-substitution pass.
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DO $bootstrap$
                DECLARE
                    user_name text := %s;
                    user_pwd text := %s;
                    schema_name text := %s;
                    db_name text := current_database();
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = user_name) THEN
                        EXECUTE format('CREATE ROLE %%I LOGIN PASSWORD %%L', user_name, user_pwd);
                        RAISE NOTICE 'created role %%', user_name;
                    ELSE
                        EXECUTE format('ALTER ROLE %%I WITH LOGIN PASSWORD %%L', user_name, user_pwd);
                        RAISE NOTICE 'role %% already exists, password updated', user_name;
                    END IF;

                    EXECUTE format(
                        'CREATE SCHEMA IF NOT EXISTS %%I AUTHORIZATION %%I',
                        schema_name, user_name
                    );
                    EXECUTE format(
                        'GRANT CONNECT ON DATABASE %%I TO %%I',
                        db_name, user_name
                    );
                END
                $bootstrap$;
                """,
                [target_user, target_password, schema],
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"PowerSync storage ready: role '{target_user}', schema '{schema}' in '{wger_db}'."
            )
        )
