# Changelog for the next release

> [!IMPORTANT]
> This release comes with some breaking changes for self-hoster. Please read carefully.

## New features

### Sync with Apple Health and Health Connect
The mobile app can now import your body metrics from Apple Health (iOS) and
Health Connect (Android). Once enabled in the settings, the data your smart
scale, blood pressure monitor, smartwatch or what other health apps record
is imported automatically and shows up alongside your manually entered entries.
At the moment we support these:

- body weight
- body fat
- lean body mass
- height
- blood pressure
- heart rate, summarised as one entry per day with the daily average, minimum
  and maximum
- resting heart rate
- blood oxygen, summarised as the daily average
- sleep, with the total per night plus the light, deep, REM and awake phases
- steps, distance and active energy, each as the daily total

Imported entries are marked as such and can only be changed or deleted in the
app they came from, otherwise they could be overwritten in a future import. You
can however still add entries by hand in every category, e.g. your blood pressure
taken from a non-connected device.

### Improvements to the Measurements
To support the data from the health sync, we have revamped the measurements. Each
category can now have a type (body fat, heart rate, etc.), so that we can e.g. show
the correct chart type. Additionally, the category list can be reordered.

It's also possible to save multi-value entries, such as the blood pressure.

Added a range selector for the period you want to look at. This should make loading
measurements be considerably faster, which is noticeable with histories of several
thousand entries.

We have also updated the available charts:
- the line chart now shows a 7-day average and a trend line besides the measured value
- the chart for body weight, body fat now shows when the different nutrition plans were active
- new bar chart, used for values such as the blood pressure
- heatmap, used for categories such as daily steps

### Body weight understands units
Every body weight entry now remembers the unit it was entered in and is converted
when needed. Previously, changing the unit in the profile from metric to imperial
silently reinterpreted all past entries.

### OAuth2 provider
wger can now act as an OAuth2 provider itself, so that other applications can let
their users log in with their wger account and access the API on their behalf. This
is switched off by default unless configured, see the docs for the setup.

* <https://wger.readthedocs.io/en/latest/administration/oauth2_provider.html>

### Python client for the API
There is now an official Python client, generated from the openAPI spec, for anyone
writing scripts or tools against a wger instance. For non-python users, the openAPI
spec was cleaned up and expanded, so you can use it to generate clients for your
language.

```bash
pip install wger-api-client
```

* <https://github.com/wger-project/api-client>

### Others
* Reworked internal structure for workout sessions. This now allows sessions to span
  midnight, and to log more than one session per day, e.g. morning  cardio and evening
  gym.
* New exercise names are checked against the existing ones during submission.
  A name too similar to an existing exercise is rejected with an error

### Bug fixes

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

## New settings
*(for self-hoster)*

* `WGER_MAX_SESSION_LENGTH_HOURS` (default 5) caps how long a workout session
  may be, now that sessions can span midnight.
* `WGER_SHOW_APP_STORE_LINKS` hides the links to the mobile app stores
* `USE_X_FORWARDED_HOST` for setups behind a reverse proxy
* `IDP_OIDC_PRIVATE_KEY` holds the signing key of the OAuth2 provider, see the
  docs for the management command that generates one.

## Breaking API changes
*(only relevant if you have your own scripts or interact with the REST API)*

### WeightEntry is gone
Under the hood, weight entries are measurements now: they live in the
official body weight category, which is created automatically.

The `/api/v2/weightentry/` endpoint will keep working during this release, so tools
like openScale do not need any changes.

### Measurement API
- Measurement categories gained `metric_type`, `parent`, `order` and
  `is_official`. There can be only one category per account and metric type,
  categories can be nested one level deep to group multi-value metrics, and
  measurements can only be added to categories that are not a group.
  `is_official` is read-only and filterable, official categories cannot be
  deleted and their `metric_type` cannot be changed.
- Measurements gained `source`, `external_id` and `extra_data`. The unit of a
  body weight entry is stored in `extra_data.unit` (`kg` or `lb`). If it is
  missing, the unit of the category applies. `extra_data` is replaced as a
  whole on PATCH, so send back the keys you want to keep.

### Workout sessions
* `/api/v2/workoutsession/` now uses `datetime_start` and `datetime_end`. The
  old `date`, `time_start` and `time_end` fields are gone from the responses and
  can no longer be filtered or sorted by. They are still accepted when writing so
  that offline writes queued by an older app version still arrive, but that is a
  temporary measure and will be removed in the next release.

* Sessions are no longer unique per user, day and routine.

* `datetime_start` and `datetime_end` support `gt`, `gte`, `lt`, `lte` and
  `date`, so a single day is selected with `?datetime_start__date=2026-01-15`
  and a range with `?datetime_start__gte=...`.

### Removed

* Removed the temporary `/api/v2/issue-refresh-token` endpoint. It existed only
  so the mobile app could exchange a permanent DRF token for a JWT refresh
  token. That migration has shipped and the app no longer calls it.

## Upgrade steps

* Pull new changes from the docker repo. There were changes to the sync rules due
  to the new measurements. It is recommended to stop the powersync service while
  the db migrations are running:
  ```
  docker compose pull 
  docker compose down powersync
  docker compose up -d web
  docker compose up -d powersync
  ```
