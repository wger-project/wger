# Generate authors list

This small script reads the commit information and generates a list of authors
and links them to their Github profile, if available. This can be run before
each release to keep the data up to date.

## Usage

Generate a token to avoid the rate limiting on the Github API:
<https://github.com/settings/personal-access-tokens> (no need to select any
permissions, we're just performing reading operations on public data)

Run the script and optionally copy the generated files to their correct locations
