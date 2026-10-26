# Changelog for the next release

> [!IMPORTANT]
> This release comes with some breaking changes for self-hoster. Please read carefully.

## New features

### Double progression
Progression requirements can now reference the top of the prescribed range via the new rules `max_repetitions` and `max_weight`, and the new `all_sets` flag requires every prescribed set to qualify. Together they enable classic double progression schemes ("work from 8 to 12 reps at a fixed weight, add weight only once all sets reach 12"), e.g. `{"rules": ["max_repetitions"], "all_sets": true}`.

### Others
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

### Bug fixes

* Deleting a routine, day, slot, or slot entry now preserves completed workout
  sessions and logs, including performed and target values. Only the references
  to deleted routine structure are cleared. Explicit session deletion and account
  deletion continue to remove the corresponding history. Apply the usual database
  migrations when upgrading; previously deleted history cannot be restored by
  this change.
* Sets with "Until Failure" or "Max Reps" but no repetitions value keep their
  unit in the routine API and show it in the set text.

## New settings
*(for self-hoster)*

* ...

## Breaking API changes
*(only relevant if you have your own scripts or interact with the REST API)*

* Creating exercises via `POST /api/v2/exercise/` now requires the `add_exercise`
  permission. Regular users should use `/api/v2/exercise-submission/`, which
  creates the exercise together with at least one translation.

## Upgrade steps

  ```bash
  docker compose pull 
  docker compose down powersync
  docker compose up -d web
  docker compose up -d powersync
  ```
