# Changelog for the next release

> [!IMPORTANT]
> This release comes with some breaking changes for self-hoster. Please read carefully.

## New features

### Double progression
Progression requirements can now reference the top of the prescribed range via the new rules `max_repetitions` and `max_weight`, and the new `all_sets` flag requires every prescribed set to qualify. Together they enable classic double progression schemes ("work from 8 to 12 reps at a fixed weight, add weight only once all sets reach 12"), e.g. `{"rules": ["max_repetitions"], "all_sets": true}`.

### Others
* Ingredient searches can opt in to prioritizing ingredients previously logged
  by the authenticated user with `prioritize_history=true`. Default and anonymous
  searches retain their existing ordering.
* `/api/v2/measurement/` accepts a `metric_type` instead of a `category` id when
  writing, and can be filtered by `metric_type` and `external_id`. Integrations
  such as scale apps no longer have to look up their category first or keep
  track of the ids of the entries they wrote.
* Exercise contributions always have an author: if none is given, the username
  is used. Everyone who edits an exercise or translation is credited as an
  author, images and videos keep the author of the file.
* The routine date sequences (`date-sequence-gym`, `date-sequence-display`) have
  a new `text_repr_short` per set: repetitions and weight only, without sets,
  RiR and rest, e.g. for notifications.
* Measurements have a new generic `device` source for data written by a wearable
  or sensor app on behalf of the user. Put vendor and model in `extra_data`. It
  is deduplicated on `external_id` and checked against the metric limits like
  every other source.
* Workout logs have an optional `notes` field, so individual sets can get a note
  (e.g. form cues or how the set felt) in addition to the notes of the session.
* Cloudflare Turnstile can be used as captcha on the registration and password
  reset forms, as an alternative to Google reCAPTCHA. The `CAPTCHA_PROVIDER`
  setting selects reCAPTCHA, Turnstile or no captcha, see the settings page in
  the docs.

### Bug fixes

* All 1RM estimates (calculated "1RM" and "1RM total" measurements, personal
  record trophies, routine statistics) now share one calculation. The reps in
  reserve of a set now also raise the estimate of the calculated measurements,
  existing curves change accordingly on their next recalculation. Personal
  records compare sets logged in lb and kg correctly and are no longer awarded
  for sets not counted in repetitions or not weighed in kg or lb. Personal
  record trophies already awarded for such sets are deleted by a migration.
* Counted messages for token expiry, confirmation links, inactive-member reminders,
  and workout-session limits now use locale-aware plural forms.
* Deleting a routine, day, slot, or slot entry now preserves completed workout
  sessions and logs, including performed and target values. Only the references
  to deleted routine structure are cleared. Explicit session deletion and account
  deletion continue to remove the corresponding history. Apply the usual database
  migrations when upgrading; previously deleted history cannot be restored by
  this change.
* Sets with "Until Failure" or "Max Reps" but no repetitions value keep their
  unit in the routine API and show it in the set text.
* The exercise and ingredient syncs no longer hang forever when the remote
  server stops answering. Requests to it now time out, see
  `WGER_REQUEST_TIMEOUT`.
* Gallery and exercise images with more than about 89 megapixels are now
  rejected on upload.
* `wger load-online-fixtures` downloads the ingredient fixture from
  `https://wger.de/media/ingredients/` instead of GitHub. A failed download now
  stops with an error instead of trying to load the error page.
* `/api/v2/trophy/progress/?include_repeatable=true` no longer reports earned
  trophies that are not repeatable as unearned.
* Creating guest accounts with demo entries is now limited to 10 per IP address
  and day. Above that, visitors get an empty guest account.

## New settings
*(for self-hoster)*

* `CAPTCHA_PROVIDER` (`none`, `recaptcha` or `turnstile`) replaces `USE_RECAPTCHA`.
  `USE_RECAPTCHA=True` keeps working for now, but `manage.py check` warns about
  it. Turnstile needs `TURNSTILE_SITE_KEY` and `TURNSTILE_SECRET_KEY`.
* `WGER_REQUEST_TIMEOUT` (default `60`): seconds to wait for an answer from a
  remote server, e.g. `WGER_INSTANCE` during the exercise and ingredient syncs,
  before giving up.
* `AWS_DEFAULT_ACL` (default empty): ACL for files uploaded to S3, e.g.
  `public-read` for buckets whose files aren't public by default.

## Breaking API changes
*(only relevant if you have your own scripts or interact with the REST API)*

* Creating exercises via `POST /api/v2/exercise/` now requires the `add_exercise`
  permission. Regular users should use `/api/v2/exercise-submission/`, which
  creates the exercise together with at least one translation.
* Uploading exercise images and videos is now rate-limited (50 images and 10
  videos per user and day, users with the `add_exercise` permission are exempt),
  and `ALLOW_UPLOAD_VIDEOS=False` now actually disables video uploads.
* `POST /api/v2/check-language/` is now rate-limited (30 requests per minute per
  user or IP address) and only checks the first 10,000 characters of the input.
* Opening the logout URL no longer logs out directly but asks for
  confirmation first, so a link on another site can't log users out (and
  delete guest accounts with their data).

## Upgrade steps

  ```bash
  docker compose pull 
  docker compose down powersync
  docker compose up -d web
  docker compose up -d powersync
  ```
