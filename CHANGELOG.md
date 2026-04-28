# Changelog for the next release

* The ingredient API filter now supports range lookups on `nutriscore`
  (`gt`, `gte`, `lt`, `lte`) in addition to `exact` and `in`, enabling queries
  like "better than C" (#2295).

* Add a new, more efficient ingredient API endpoint (`/api/v2/ingredient-sync`)
  for synchronizing the local database with an upstream wger server (note that
  this is a fallback, the regular sync is still via the db dump)
