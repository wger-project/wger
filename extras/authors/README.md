# Generate authors list

This small script reads the commit information and generates a list of authors
and links them to their GitHub profile, if available. This can be run before
each release to keep the data up to date.

## Usage

Note that you might run into rate-limiting issues if you run this script too
often. If so, you can generate a token and use it in the script:
<https://github.com/settings/personal-access-tokens> (no need to select any
permissions, we're just performing reading operations on public data)

Run the script and optionally copy the generated files to their correct locations

```bash
uv run generate_authors_api.py
```
