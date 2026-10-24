# wger Django backend

Django + DRF, dependency management via `uv`, lint/format via `ruff`. Tests use Django's built-in test runner. The
React frontend (`../react`) and the Flutter app (`../flutter`) are clients of this server's REST API and PowerSync
endpoints.

## Verify after edits

- `DJANGO_SETTINGS_MODULE=settings.ci uv run ./manage.py test wger.<app> --parallel auto`: scope to the app you changed,
  the full suite is slow. `settings.ci` is what CI runs (SQLite, no migrations), always use it for tests.
- `uv run ruff check wger/<path>`: lint
- `uv run ruff format wger/<path>`: format
- After model changes: `uv run ./manage.py makemigrations --check`

Run the relevant ones for what you changed; comment- or docstring-only edits don't need a test run.

For migrations: also test on a production-like DB copy when possible. Never run destructive migrations (`flush`, drop,
schema reset) without asking.

## Dev setup

- `uv sync --group dev` installs everything. Never run `isort`: it was replaced by ruff and rewrites every import of the
  file it touches. A stale copy may still sit in an old venv, `uv sync` removes it.
- `wger-dev` in `.claude/launch.json` runs `manage.py runserver 8100` with `settings.local_dev` (SQLite, `DEBUG=True`).
- Settings live in `settings/`, not inside `wger/`: `settings_global.py` (base), `local_dev.py`, `ci.py`, `main.py`
  (production, configured via env vars). `settings/*_extra.py` is gitignored for local overrides.
- `.mcp.json` configures the wger MCP server.

## Layout

```
wger/<app>/
├── models/        one file per model (or group), re-exported from models/__init__.py
├── api/           DRF serializers, viewsets, filtersets
├── views/         classic Django views (server-rendered pages, admin-ish forms)
├── powersync.py   upload handlers for the app's PowerSync-synced tables
├── tasks.py       Celery tasks
├── signals.py     cross-cutting post_save/post_delete handlers
├── management/    management commands (syncs, maintenance)
├── fixtures/      JSON fixtures, test-*.json for tests
├── migrations/
├── templates/
└── tests/         test_*.py
```

| App              | Purpose                                                                         |
|------------------|---------------------------------------------------------------------------------|
| **manager**      | Workout routines, sessions, logs, scheduling, weight/rep configs                |
| **exercises**    | Exercise database (wiki-style), images, videos, muscles, categories, variations |
| **nutrition**    | Meal plans, ingredients, nutrition diary, Open Food Facts sync                  |
| **core**         | User profiles, languages, licenses, repetition units, weight units              |
| **measurements** | Body measurement categories and entries, incl. body weight                      |
| **weight**       | Compatibility surface for body weight, no models (see measurements)             |
| **gallery**      | Progress photos                                                                 |
| **gym**          | Gym/facility management                                                         |
| **trophies**     | Achievement system                                                              |
| **mailer**       | Email notification queue                                                        |
| **utils**        | Shared helpers, middleware, viewset/permission/pagination base classes          |

- All API endpoints live under `/api/v2/`, registered on a `DefaultRouter`. Auth: allauth headless + SimpleJWT, plus
  legacy API tokens. Schema at `/api/v2/schema/ui` (drf-spectacular).
- **Ownership:** user-owned models implement `get_owner_object()`; permission checks and the PowerSync upload
  (`check_fk_ownership` in `wger/utils/viewsets.py`) rely on it. New user-owned models need it too.
- `simple_history` tracks the exercise models; a field change there also changes the historical table in the migration.

## Stack-specific rules

- **The API schema is a contract.** Both clients and the generated python client are written against it. After a
  serializer, filter or endpoint change, check whether `../react` and `../flutter` need the same change and say so.
  `@action` endpoints need an explicit `@extend_schema(responses=...)`, otherwise the schema shows the wrong shape.
- **API changes bump the dev version:** if a change touches the REST API in any meaningful way (new or changed endpoint,
  field, accepted value, validation or response shape), increment the `dev.N` suffix of `VERSION_STRING` in
  `wger/version.py` in the same change, e.g. `2.8.0-dev.0` to `2.8.0-dev.1`. Clients can then tell which dev build has
  the feature. Keep the semver form `-dev.N` (see the docstring there). Small changes (a different validation error,
  etc.) can stay, when in doubt just ask.
- **PowerSync:** clients read synced tables from a local copy and write them back through `wger/<app>/powersync.py`.
  A new field or table on a synced model needs the sync rules in the docker repo
  (`../docker/services/config-powersync/sync_rules.yaml`) and the upload handler updated. Rows that already exist on a
  device keep NULL for a new column until they are downloaded again, so either backfill in a data migration (touching
  the rows) or keep the column nullable/defaulted on the client side (see the flutter AGENTS.md).
- **Dates and time zones:** `USE_TZ = True`, `TIME_ZONE = 'UTC'`; store instants as aware datetimes
  (`django.utils.timezone`), never naive ones. "Which calendar day" questions use the owner's
  `UserProfile.timezone`, not the zone of the request; empty means unknown. Use `DateField` for calendar days and
  `DateTimeField` for instants, the clients map them differently.
- **Malformed IDs:** serializers and django-filter already answer bad IDs with 400. Manual lookups in viewsets or
  filters (`int(request.GET[...])`, `UUID(...)`) need a guard, otherwise they end up as 500.
- **Celery:** production runs with Celery, but `USE_CELERY=False` is supported, so a task must also work when called
  inline.
- **i18n:** user-visible strings go through `gettext`/`{% translate %}`. Translations come from Weblate, don't edit the
  `.po` files of other languages. If a client already has the string, reuse its English text exactly.
- **Logs:** never log secrets at any level (tokens, passwords, auth response bodies).
- **Secrets / debug flags:** never commit a real `SECRET_KEY` or leave `DEBUG=True` in non-test config.
- **Install/config changes:** new env vars, settings or docker changes also need the documentation in `../docs`
  (readthedocs) updated.

## Migration & data changes

- **Existing bad data:** schema changes that add NOT NULL or unique constraints must include a data migration that fixes
  existing rows, not just the schema. Never assume the table is clean.
- **Unreleased migrations:** if a migration was added on the current branch / since the last release, edit it instead of
  stacking a new one on top, then verify with `makemigrations --check`.
- **Callable defaults:** `default=uuid.uuid4`, `default=timezone.now`, never `default=uuid.uuid4()` (evaluated once at
  import time). Same rule for any default that produces a fresh value.
- **Unique constraints:** if a model has a unique constraint, audit *every* call site that creates an instance
  (`grep -rn "ModelName.objects.create\|ModelName(" --include="*.py"`). All sites should use `update_or_create` /
  `get_or_create`. Don't fix only the failing one.
- **Triggers / signals:** when adding `post_save` handlers or DB triggers, walk through one example transaction and check
  ordering / recursion before declaring done.

## Tests

- **Base classes:** `WgerTestCase`, `WgerAddTestCase`, `WgerEditTestCase`, `WgerDeleteTestCase`, `WgerAccessTestCase`
  in `wger/core/tests/base_testcase.py`; `ApiBaseResourceTestCase` and the `Api*TestCase` mixins in
  `wger/core/tests/api_base_test.py`. Use them, and the `test-*.json` fixtures, instead of building setup by hand.
- **Cross-cutting API tests as mixins:** wire a new behavior check into the existing per-model `*CustomApiTestCase`
  via a mixin instead of duplicating URLs and payloads in a new class.
- **Bug fixes need regression tests** that fail on the old code and pass on the new.
- **Prove a test can fail.** After writing one, break the production side it guards and watch it go red, then restore.
- **URLs via `reverse('namespace:name')`**, not hard-coded `/api/v2/...` strings.
- **Don't test library behavior.** No tests that only exercise DRF or django-filter defaults; test custom methods and
  overrides.
- **Dates:** timezone-aware datetimes only. Test the boundary days of a date range (start day, end day, the day after)
  and ranges across a DST switch, which has 23 or 25 hours.
- **No hard-coded PKs** in test data; SQLite and Postgres assign them differently, also with `bulk_create`.
- **Mock at the usage site** (`wger.app.module.name`), not where the name is defined.
- **Docstrings state what is verified**, no bug history ("Regression: ...") and no justification for the test's
  existence.

## Code style

- Line length 100, single quotes, formatter `ruff format`.
- Imports sorted by ruff's isort rules (`I`), section order `FUTURE → STDLIB → DJANGO → THIRDPARTY → FIRSTPARTY →
  LOCAL`, each with a heading comment. The `I` rule is off for migrations, `settings/`, `extras/` and `apps.py`. Ruff
  never explodes an import into one name per line by itself but keeps an existing magic trailing comma; write new
  multi-name imports in that exploded style by hand.
- Comments and docstrings in English and short: one line where one does, comment only what the code can't express. The
  derivation belongs in the commit message or the test. No em-dashes, use a period, colon or parentheses.
- Type hints on new helpers with plain types; skip them where they would need generics, `TypeVar` or `Protocol`.

## Other rules

- **Visible changes go into CHANGELOG.md:** if a feature, behavior change or bug fix is noticeable for users,
  self-hosters or API clients, add a short entry to the matching section of `CHANGELOG.md` in the same change.
  Internal refactors and small fixes don't need one, when in doubt just ask.
- **No advisory IDs** (GHSA etc.) in code, comments or commit messages.

## Scope

Make the minimum change requested. Don't refactor adjacent code, rename things, or change defaults unless explicitly
asked. Mention adjacent issues as follow-ups instead of fixing them inline.

When programming for special cases, either ask or check first how probable they are (rare race conditions, parallel
usage of the app with different devices, etc.).
