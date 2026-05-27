# Changelog for the next release

> [!IMPORTANT]
> This release comes with several breaking changes. Please read carefully.

## New features

### Offline mode (mobile app) 🥳

Adds the necessary backend changes to (finally!) support offline mode in the
mobile app. The data is saved in a local sqlite database and synced with the
server when the network is reachable again. Basically the whole application
can be used without internet, with few exceptions such as

* routines (needs some backend logic to calculate the routine data)
* gallery (due to the image upload)
* account actions like changing the email, etc.

Buttons and menus will be grayed out if they can't currently be used.

### Social login and 2FA

It's now possible to login with social auth providers like Google, Facebook, etc.
Also, we now support two-factor authentication like security codes or passkeys.

* https://wger.readthedocs.io/en/latest/administration/mfa.html
* https://wger.readthedocs.io/en/latest/administration/social_auth.html


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

* If you are using docker, make sure to pull the latest changes from the 
  [docker repo](https://github.com/wger-project/docker) as there is a new service
  ("powersync") and configs (e.g. for nginx/Caddy).

* `SIGNING_KEY` is replaced by `JWT_PRIVATE_KEY` and `JWT_PUBLIC_KEY`.
  Run `docker compose exec web ./manage.py generate-jwt-keys` to generate a new pair.

* The new powersync service needs its own dedicated user and schema inside the
  Postgres database to store its sync state, run
  `docker compose exec web ./manage.py setup-powersync-storage` to apply.
  If you want to change the defaults, this can be configured in `PS_STORAGE_PG_URI`.

* Make sure you have set `SITE_URL` with your server's URL

* *(ignore if you didn't change the db password)* Set the `PS_DATABASE_URI` with
  the wger db password in the usual format `postgres://<user>:<password>@<host>:<port>/<dbname>`.

* *(ignore if you didn't change the db password)* The Postgres container in the
  docker-compose setup now reads its credentials (`POSTGRES_USER`, `POSTGRES_PASSWORD`,
  `POSTGRES_DB`) from `prod.env` instead  of having them hardcoded in the yaml file.

## Breaking changes

*(only relevant if you have your own scripts or interact with the REST API)*

The type for the ID was changed from integer to string (UUID) for several models,
to allow clients to generate IDs locally. This affects the following endpoints:
* `/api/v2/measurement-category/`
* `/api/v2/measurement/`
* `/api/v2/nutritionplan/` and `/api/v2/nutritionplaninfo/`
* `/api/v2/meal/`
* `/api/v2/mealitem/`
* `/api/v2/nutritiondiary/`
* `/api/v2/workoutsession/`
* `/api/v2/workoutlog/`

**`/api/v2/login/` and `/api/v2/register/` endpoints removed.** These endpoints returned
a permanent token, use the allauth ones instead (JWT based).  If you still need a permanent
one, visit the "API key" page in the user settings and paste it into scripts.

**`/api/v2/token` endpoint removed.** Exchanging username + password for a JWT
pair via this endpoint bypassed 2FA. To get tokens, either use
`/_allauth/app/v1/auth/login` (which respects the MFA challenge flow) or mint
a long-lived refresh token from the "API key" page in the user settings.
