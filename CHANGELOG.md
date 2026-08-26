# Changelog for the next release

## New features

* Improved openAPI spec. The spec now properly describes the different parts of
  the API and can be used to generate clients.
* Emails are now send asynchronously via the celery queue, this should make
  registration, password resets, etc. feel a bit snappier. If celery is not configured,
  the emails are send as before
* Faster and stronger password hashing: passwords are now hashed with argon2 instead
  of PBKDF2. Argon2 is what Django itself recommends, but PBKDF2 is only the default
  because it needs no additional library. Existing passwords keep working and are
  migrated automatically on the next login.

### OAuth2 provider

wger can now act as an OAuth2 provider itself, so that other applications can let
their users log in with their wger account and access the API on their behalf. This
is switched off by default unless configured, see the docs for the setup.

* <https://wger.readthedocs.io/en/latest/administration/oauth2_provider.html>

## Bug fixes

* Ingredient search now finds matching words in long ingredient names and ranks
  more relevant results first
* Exercise search now finds matching words in long exercise names, e.g. "curl"
  finds "Alternating Biceps Curls With Dumbbell", and sorts the results by
  relevance
* Gated progressions (configs with `requirements`) now advance exactly one step
  per qualifying workout instead of back-filling increments for skipped,
  non-qualifying iterations
* Gated progressions now reach configs scheduled for later iterations, so
  multi-phase plans (e.g. bigger increments from week 6 on) work when the
  requirements are only met intermittently
* Ungated configs no longer back-apply increments of earlier gated configs
  whose requirements were never met
* Progression requirements are now checked against the rounded values as they
  are displayed, so reaching the shown prescription always counts
* The min and max configs of a field now advance together, following the
  requirements of the base config
