# Changelog for the next release

> [!IMPORTANT]
> This release comes with some breaking changes for self-hoster. Please read carefully.

## New features

### Double progression
Progression requirements can now reference the top of the prescribed range via the new rules `max_repetitions` and `max_weight`, and the new `all_sets` flag requires every prescribed set to qualify. Together they enable classic double progression schemes ("work from 8 to 12 reps at a fixed weight, add weight only once all sets reach 12"), e.g. `{"rules": ["max_repetitions"], "all_sets": true}`.


### Others
* 

### Bug fixes

* 

## New settings
*(for self-hoster)*

* 

## Breaking API changes
*(only relevant if you have your own scripts or interact with the REST API)*

## Upgrade steps

  ```bash
  docker compose pull 
  docker compose down powersync
  docker compose up -d web
  docker compose up -d powersync
  ```
