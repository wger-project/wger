# Changelog for the next release

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
