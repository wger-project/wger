# Changelog for the next release

## Upgrade steps

* Some unused thumbnail sizes have been deleted, run `./manage.py prune-thumbnails`
  to delete dangling files

* The default location for ingredient images has changed. Please run
  `./manage migrate-ingredient-image-paths` to migrate existing entries. Note
  that this is technically optional, as the old paths will continue working,
  but it is advised for consistency.

* Set the `PS_DATABASE_URI` with the wger db password in the usual format
  `postgres://<user>:<password>@<host>:<port>/<dbname>`. Note that if you didn't
  change the default db config, you just need to update the docker compose files,
  and you're good to go.

* The Postgres container in the docker-compose setup now reads its credentials
  (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) from `prod.env` instead
  of having them hardcoded in `services/postgres.yaml`. As above, you only need
  to change this if you are using some non-standard password.

## Powersync

Adds powersync support. This allows clients (i.e. the mobile app) to finally
implement offline support. The data is saved in a local sqlite database and
synced with the server when possible.

Incompatible changes:

The type for the ID for Measurement and MeasurementCategory was changed from integer
to UUID. This was made to allow for clients to generate IDs locally and affects
`/api/v2/measurement-category/` and `/api/v2/measurement/`.

Make sure you have set the values for `SITE_URL`.

## Other changes

* The exercise image API now exposes `thumbnails` with `small` and `medium`
  URLs, consistent with the ingredient API

* The ingredient API filter now supports range lookups on `nutriscore`
  (`gt`, `gte`, `lt`, `lte`) in addition to `exact` and `in`, enabling queries
  like "better than C" (#2295).

* Add a new, more efficient ingredient API endpoint (`/api/v2/ingredient-sync`)
  for synchronizing the local database with an upstream wger server (note that
  this is a fallback, the regular sync is still via the db dump)

* JWT refresh tokens now rotate on every use. Combined with blacklist-after-rotation
  this makes refresh tokens single-use and lets a leaked token live only until
  the next refresh call. It's recommended to update your `prod.env` and set
  `REFRESH_TOKEN_LIFETIME` to a value like 3000.

* When a username is already taken during registration, the system now suggests available
  alternatives. This replaces the default DRF UniqueValidator with a custom validator that
  includes suggested usernames in the error response. Suggestions are supported in both the
  serializer and web registration form validation.
  
* Exercise language are now also checked when performing edits, instead of only
 during submission.
