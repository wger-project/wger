# Changelog for the next release

> [!IMPORTANT]
> This release comes with several breaking changes. Please read carefully.

## New features

### Offline mode (mobile app)

Adds the necessary backend changes to (finally!) support offline mode in the
mobile app. The data is saved in a local sqlite database and synced with the
server when the network is reachable again.

The downside to this is that there are a handful of manual steps needed, see below.

### Social login and 2FA

It's now possible to login with social auth providers like Google, Facebook, etc.

*****
!!! TODO !!!: add link to readthedocs
*****

Also, we now support two-factor authentication like security codes or passkeys.

### Others

* The ingredient API filter now supports range lookups on `nutriscore`
  (`gt`, `gte`, `lt`, `lte`) in addition to `exact` and `in`, enabling queries
  like "better than C" (#2295).

* Add a new, more efficient ingredient API endpoint (`/api/v2/ingredient-sync`)
  for synchronizing the local database with an upstream wger server (note that
  this is a fallback, the regular sync is still via the db dump which is faster)

* JWT refresh tokens now rotate on every use. Combined with blacklist-after-rotation
  this makes refresh tokens single-use and lets a leaked token live only until
  the next refresh call. It's recommended to update your `prod.env` and set
  `REFRESH_TOKEN_LIFETIME` to a value like 3000.

* The exercise language is now also checked when performing edits, instead of only
  during submission so it's not possible to e.g. save a Spanish text for the English
  description.


## Upgrade steps

* If you are using docker, make sure to pull the latest changes from the docker repo
  as there is a new service ("powersync") and configs (e.g. for nginx/Caddy).

* Set the `PS_DATABASE_URI` with the wger db password in the usual format
  `postgres://<user>:<password>@<host>:<port>/<dbname>`. Note that if you didn't
  change the default db config, you just need to update the docker compose files,
  and you're good to go.

* The Postgres container in the docker-compose setup now reads its credentials
  (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`) from `prod.env` instead
  of having them hardcoded in the yaml file. As above, you only need to change
  this if you are using some non-standard password.

* `SIGNING_KEY` is replaced by `JWT_PRIVATE_KEY` and `JWT_PUBLIC_KEY`.
  Run `docker compose exec web ./manage.py generate-jwt-keys` to generate a new pair.

* The powersync service needs its own dedicated user and schema inside the Postgres
  database to store its sync state, this can be configured in `PS_STORAGE_PG_URI`
  if you want to change the defaults. Afterwards just run
  `docker compose exec web ./manage.py setup-powersync-storage` to apply.

* Make sure you have set the value for `SITE_URL`.

## Breaking changes

The type for the ID for Measurement and MeasurementCategory was changed from integer
to string (UUID). This was made to allow for clients to generate IDs locally and affects
`/api/v2/measurement-category/` and `/api/v2/measurement/`.

**`/api/v2/login/` endpoint removed.** This endpoint returned a permanent token
If you want to generate a new token, visit the "API key" page in the user settings
and paste it into scripts.

**`/api/v2/token` endpoint removed.** Exchanging username + password for a JWT
pair via this endpoint bypassed 2FA. To get tokens, either use
`/_allauth/app/v1/auth/login` (which respects the MFA challenge flow) or mint
a long-lived refresh token from the "API key" page in the user settings.
