# Changelog for the next release

## New features

### Others

* Reworked internal structure for workout sessions. This now allows sessions to span
  midnight, and to log more than one session per day, e.g. morning  cardio and evening
  gym.

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
