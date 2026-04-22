# Changelog for the next release

## Powersync

Adds powersync support. This allows clients (i.e. the mobile app) to finally 
implement offline support. The data is saved in a local sqlite database and 
synced with the server when possible.

Incompatible changes:

The type for the ID for Measurement and MeasurementCategory was changed from integer
to UUID. This was made to allow for clients to generate IDs locally and affects
`/api/v2/measurement-category/` and `/api/v2/measurement/`.

Make sure you have set the values for `SITE_URL`.

## Others
