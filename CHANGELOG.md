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

* Add support for dynamic measurement categories. The (`/api/v2/measurement/`) endpoint now
  intercepts requests for dynamic categories (such as BMI) and auto-calculates the
  results on-the-fly using existing user data (e.g., profile height and weight entries).
  A new endpoint at (`/api/v2/measurement-category/dynamic-types/`) has been added to
  expose the available dynamic options.
  An enum is used for the different options and can be extended for more dynamic types.