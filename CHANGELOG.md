# Changelog for the next release

Improved ingredient sync. Instead of loading the ingredients over the paginated
API (which was taking a long time with almost 3 million entries), wger instances
can generate and read a dump file, which can be processed much more effectively.
The setting `SYNC_INGREDIENTS_CELERY` will automatically prefer the bulk dump
over the paginated API, falling back to the API if no dump is available.

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

<https://github.com/wger-project/wger/issues/2124>
Automatically read the date from uploaded image to the gallery.

Improve serving size support for ingredients. Users can now log food in
everyday units like "1 Serving (2 biscuits)" or "1 Cup" instead of only grams,
with serving sizes automatically imported from Open Food Facts.
The `/api/v2/weightunit/` endpoint has been removed.
