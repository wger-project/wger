# Changelog for the next release

## Sync with Apple Health and Health Connect

The mobile app can now import your body metrics from Apple Health (iOS) and
Health Connect (Android). Once enabled in the settings, the data your smart
scale, blood pressure monitor, smawr watch or what other health apps record
is imported automatically and shows up alongside your manually entered entries.
At the moment we support these:

- body weight
- body fat
- height
- blood pressure
- heart rate, summarised as one entry per day with the daily average, minimum
  and maximum)
- resting heart rate
- sleep, with the total per night plus the light, deep, REM and awake phases

Imported  entries are marked as such and can only be changed or deleted in the
app they came from, otherwise they could be overwritten in a future import. You
can however still add entries by hand in every category, e.g. your blood pressure
taken from a non-connected device.

## Body weight understands units
Every body weight entry now remembers the unit it was entered in and is converted
when needed. Previously, changing the unit in the profile from metric to imperial
silently reinterpreted all past entries.

## Improvements to the Measurement

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


## Breaking API changes

### WeightEntry is gone

Under the hood, weight entries are measurements now: they live in the
official body weight category, which is created automatically.

Weight entry ids are now UUIDs instead of numbers. Existing entries keep the
id they already had.

The `/api/v2/weightentry/` endpoint will keep working during this release, so tools
like openScale do not need any changes.

### API

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
