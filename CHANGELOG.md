# Changelog for the next release

## Powersync

Adds powersync support. This allows clients (i.e. the mobile app) to finally 
implement offline support. The data is saved in a local sqlite database and 
synced with the server when possible.

Incompatible changes:

The type for the ID for Measurement and MeasurementCategory was changed from integer
to UUID. This was made to allow for clients to generate IDs locally and affects
`/api/v2/measurement-category/` and `/api/v2/measurement/`.

## Others

<https://github.com/wger-project/wger/issues/2231> Add vegan and vegetarian flags to
the ingredient model. This allows to filter products based on dietary preferences.
The unused `/api/v2/ingredient/search/` API endpoint has been removed.

<https://github.com/wger-project/wger/pull/2222> Add flag for exercise images indicating
whether the image was AI generated. This is currently not used, but can be used in the
future if we rework the images,

Add "warmup" to list of set types.

<https://github.com/wger-project/wger/pull/2137>
Add more information to the repetition units in the routines. This will allow
us to e.g. properly handle time units in the mobile app, e.g.  by showing a
timer or similar. The `setting-repetitionunit` endpoint now exposes the new fields
`unit_type` and `multiplier`.
