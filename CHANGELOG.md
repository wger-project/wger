# Changelog for the next release

## New features

* Improved openAPI spec. The spec now properly describes the different parts of
  the API and can be used to generate clients.

### OAuth2 provider

wger can now act as an OAuth2 provider itself, so that other applications can let
their users log in with their wger account and access the API on their behalf. This
is switched off by default unless configured, see the docs for the setup.

* <https://wger.readthedocs.io/en/latest/administration/oauth2_provider.html>

### Others

* Reworked internal structure for workout sessions. This now allows sessions to span
  midnight, and to log more than one session per day, e.g. morning  cardio and evening
  gym.

## Bug fixes

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

## Breaking changes

*(only relevant if you have your own scripts or interact with the REST API)*

**`/api/v2/workoutsession/` now uses `datetime_start` and `datetime_end`.** The
old `date`, `time_start` and `time_end` fields are gone from the responses and
can no longer be filtered or sorted by. They are still accepted when writing so
that offline writes queued by an older app version still arrive, but that is a
temporary measure and will be removed in the next release.

* Sessions are no longer unique per user, day and routine.

* `datetime_start` and `datetime_end` support `gt`, `gte`, `lt`, `lte` and
  `date`, so a single day is selected with `?datetime_start__date=2026-01-15`
  and a range with `?datetime_start__gte=...`.

## Removed

* Removed the temporary `/api/v2/issue-refresh-token` endpoint. It existed only
  so the mobile app could exchange a permanent DRF token for a JWT refresh
  token. That migration has shipped and the app no longer calls it.
