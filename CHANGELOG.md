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
- the line chart now shows a moving average and a trend line besides the measured value
- the chart for body weight, body fat now shows when the different nutrition plans were active
- new bar chart, used for values such as the blood pressure
- heatmap, used for categories such as daily steps
- new change chart, one bar per week showing how far the value moved in it
- new distribution chart, showing how often each value occurred, with the median
  and the newest reading marked

Which chart a category gets follows from its type, but you can also pick it yourself
when you edit the category. Only the charts that suit the type are offered, and a
group is always drawn from what its components are.

### Calculated categories
A measurement category can now be calculated by wger instead of typed in by you.
At the moment there's available:

- BMI, from your body weight entries and the height
- waist to height ratio, from a category you measure your waist in
- the one-rep max of an exercise, estimated from your logged sets
- the total of two to five exercises, the classic being bench press, squat and
  deadlift added up

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

### Your own timezone
Streaks, calendar days and trophies are now calculated in your own timezone.
The apps report it automatically, until they have, or for accounts that only
ever use scripts, the server's timezone is used like before.

### Others
* Reworked internal structure for workout sessions. This now allows sessions to span
  midnight, and to log more than one session per day, e.g. morning  cardio and evening
  gym.
* New exercise names are checked against the existing ones during submission.
  A name too similar to an existing exercise is rejected with an error
* Improved openAPI spec. The spec now properly describes the different parts of
  the API and can be used to generate clients.
* Emails are now send asynchronously via the celery queue, this should make
  registration, password resets, etc. feel a bit snappier. If celery is not configured,
  the emails are send as before
* Faster and stronger password hashing: passwords are now hashed with argon2 instead
  of PBKDF2. Argon2 is what Django itself recommends, but PBKDF2 is only the default
  because it needs no additional library. Existing passwords keep working and are
  migrated automatically on the next login.

### Bug fixes

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
- Categories gained `dynamic_type` and `dynamic_params` for the calculated
  categories described above. `/api/v2/measurement-category/dynamic-types/`
  lists what the server can calculate and which parameters each category takes.
  Only free-form categories without entries of their own can be calculated,
  and the calculation cannot be changed once it is set.
- `source` gained the value `calculated` for the entries such a category holds.
  They are refused on POST, PATCH and DELETE, since the server replaces them
  whenever what they are computed from changes.

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

### Userprofile
* New field `time_zone` on `/api/v2/userprofile/` for the user's IANA timezone
  name, e.g. `America/Toronto`. Date sensitive calculations, like the trophies
  are done using this value.

### Removed

* Removed the temporary `/api/v2/issue-refresh-token` endpoint. It existed only
  so the mobile app could exchange a permanent DRF token for a JWT refresh
  token. That migration has shipped and the app no longer calls it.

## Upgrade steps

* Make sure `TIME_ZONE` is set correctly **before** upgrading, and treat it as
  fixed afterwards. The migration converts the old session dates using this
  zone, and it stays the fallback for users whose apps have not reported their
  own one yet. Changing it later shifts those users' past training days.
* Pull new changes from the docker repo. There were changes to the sync rules due
  to the new measurements. It is recommended to stop the powersync service while
  the db migrations are running:
  ```bash
  docker compose pull 
  docker compose down powersync
  docker compose up -d web
  docker compose up -d powersync
  ```
