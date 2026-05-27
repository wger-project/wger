# Changelog for the next release

## Upgrade steps

* Some unused thumbnail sizes have been deleted, run `./manage.py prune-thumbnails`
  to delete dangling files

* The default location for ingredient images has changed. Please run
  `./manage migrate-ingredient-image-paths` to migrate existing entries. Note
  that this is technically optional, as the old paths will continue working,
  but it is advised for consistency.

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
