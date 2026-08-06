# Changelog for the next release

* Added a `Routine.objects.active()` manager method and a
  `GET /api/v2/routine/current/` endpoint that returns the routine currently
  running (today within its start/end dates) instead of the most recently
  created one, falling back to the latter when none is active (#2361)
