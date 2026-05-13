# Standard Library
import datetime
import json
import os
import re
import shutil
from dataclasses import dataclass
from getpass import getpass
from pathlib import Path

# Third Party
import requests

# /// script
# dependencies = [
#   "requests",
# ]
# ///

# Run with "uv run generate_authors_api.py". To generate a token, go to https://github.com/settings/tokens

ORGANIZATION = 'wger-project'
REPOSITORIES = ['wger', 'flutter', 'react', 'docker', 'docs']
COMMITS_PER_PAGE = 100
CACHE_DIR = Path('commits_cache')

# Commit authors whose contributions we don't credit (matched as substrings).
BOT_AUTHORS = ('dependabot', 'github-actions')


@dataclass
class Person:
    """A contributor or translator, normalized from GitHub commit data."""

    name: str
    email: str
    username: str = ''
    """GitHub login, empty when the email isn't linked to a GitHub account"""

    def __post_init__(self):
        # Some commits have a raw email address in the author "name" field.
        if '@' in self.name:
            self.name = self.name.replace('@', ' [at] ')

    @property
    def github_url(self) -> str:
        """GitHub profile URL if the person has a linked account, empty otherwise."""
        return f'https://github.com/{self.username}' if self.username else ''

    @property
    def identity_key(self) -> tuple[str, str]:
        """Stable key for cross-repo deduplication: by username when known, else email."""
        return ('user', self.username) if self.username else ('email', self.email)


def get_github_token() -> str:
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        token = getpass('Enter your GitHub token: ')

    return token


def fetch_commits_from_github(repo_name: str, token: str) -> list[dict]:
    """Fetch commits with an incremental, append-only cache.

    On first run, paginates the whole history and caches each API response.
    On later runs, reads the latest cached commit's date and uses GitHub's
    ``since`` query parameter to fetch only commits newer than that.
    """
    repo_cache_dir = CACHE_DIR / repo_name
    repo_cache_dir.mkdir(parents=True, exist_ok=True)

    # Load any cached commits from previous runs
    cached_pages = sorted(
        repo_cache_dir.glob('page_*.json'),
        key=lambda p: int(p.stem.split('_')[1]),
    )
    cached_commits: list[dict] = []
    for cache_file in cached_pages:
        with open(cache_file) as f:
            cached_commits.extend(json.load(f))

    # If we have a cache, only request commits newer than the latest one
    since_param = None
    if cached_commits:
        latest_iso = max(c['commit']['author']['date'] for c in cached_commits)

        # +1s so the boundary commit isn't returned again (GitHub's `since` is inclusive)
        cutoff = datetime.datetime.fromisoformat(
            latest_iso.replace('Z', '+00:00')
        ) + datetime.timedelta(seconds=1)
        since_param = cutoff.strftime('%Y-%m-%dT%H:%M:%SZ')
        print(f'Cache: {len(cached_commits)} commits loaded, fetching anything since {since_param}')

    url = f'https://api.github.com/repos/{ORGANIZATION}/{repo_name}/commits'
    headers = {'Authorization': f'token {token}'} if token else {}
    base_params: dict = {'per_page': COMMITS_PER_PAGE}
    if since_param:
        base_params['since'] = since_param

    # Paginate until we run out of results
    new_commits: list[dict] = []
    page = 1
    while True:
        try:
            response = requests.get(url, headers=headers, params={**base_params, 'page': page})
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as e:
            print(f'Error fetching commits: {e}')
            return cached_commits  # still return what we have
        if not data:
            break
        new_commits.extend(data)
        print(f'Fetched page {page} ({len(data)} commits)')
        if len(data) < COMMITS_PER_PAGE:
            break
        page += 1

    # Append the new commits as additional cache files (oldest pages keep their numbers)
    if new_commits:
        next_seq = len(cached_pages) + 1
        for i in range(0, len(new_commits), COMMITS_PER_PAGE):
            chunk = new_commits[i : i + COMMITS_PER_PAGE]
            with open(repo_cache_dir / f'page_{next_seq}.json', 'w') as f:
                json.dump(chunk, f, indent=4)
            next_seq += 1
        print(f'Cached {len(new_commits)} new commits')

    return cached_commits + new_commits


def extract_contributors(
    repo_name: str, token: str
) -> tuple[list[Person], dict[str, list[Person]]]:
    """Retrieves contributors and translators from the GitHub API.

    Returns a flat list of contributors and a dict of language -> translators.
    Both are pre-deduplicated within the repo by author email.
    """

    # Use dicts keyed by email for per-repo pre-dedupe, then return as lists
    # so callers don't depend on the internal key.
    contributors: dict[str, Person] = {}
    translators: dict[str, dict[str, Person]] = {}

    for commit in fetch_commits_from_github(repo_name, token):
        commit_message = commit['commit']['message']

        # commit['author'] (the GitHub user) is null when the committer isn't
        # linked to a GitHub account. The inner commit.author fields always
        # carry the raw git name/email from the commit object.
        github_author = commit.get('author', {})
        username = github_author.get('login', '') if github_author else ''
        name = commit['commit']['author']['name']
        email = commit['commit']['author']['email']

        if any(bot in name for bot in BOT_AUTHORS):
            continue

        # Weblate's bot account commits on behalf of the actual translator —
        # linking to the bot's GitHub profile would be misleading.
        if username == 'weblate':
            username = ''

        person = Person(name=name, email=email, username=username)

        language_match = re.search(r'Translated using Weblate \((.+)\)', commit_message)
        if language_match:
            language = language_match.group(1)
            translators.setdefault(language, {})[email] = person
        else:
            contributors[email] = person

    return (
        list(contributors.values()),
        {lang: list(people.values()) for lang, people in translators.items()},
    )


def deduplicate(people: list[Person]) -> list[Person]:
    """
    Merge entries that refer to the same person.

    Pass 1: same GitHub username (or same email when no username) → one entry,
    preferring the one with a username.

    Pass 2: drop no-username entries whose name matches a known username entry.
    Catches the case where the same person committed from both their
    GitHub-linked email *and* an unlinked one.

    Trade-off: two distinct contributors with identical names but different
    link states will collapse into one; with diverse real names this should be
    rare in practice.
    """

    # Pass 1: identity-based dedupe (username when available, else email)
    seen: dict[tuple[str, str], Person] = {}
    for p in people:
        key = p.identity_key
        if key not in seen or (p.username and not seen[key].username):
            seen[key] = p

    # Pass 2: collapse no-username entries onto same-named username entries
    named = {p.name.lower() for p in seen.values() if p.username}
    return [p for p in seen.values() if p.username or p.name.lower() not in named]


def generate_markdown(p: Person) -> str | None:
    """Generate a single markdown bullet for a contributor or translator."""

    if not p.name:
        return None
    if p.username:
        return f'- {p.name} - [{p.github_url}]({p.github_url})\n'
    return f'- {p.name}\n'


def generate_rst_entry(p: Person) -> str | None:
    """Generate a single RST bullet for a contributor or translator."""

    if not p.name:
        return None
    if p.username:
        return f'* {p.name} — {p.github_url}\n'
    return f'* {p.name}\n'


def generate_authors_file(
    repo_name: str,
    contributors: list[Person],
    translators: dict[str, list[Person]],
    output_file: str = 'AUTHORS.md',
):
    """Generates a Markdown file with contributors and translators for one repo."""
    filename = f'{repo_name}-{output_file}'

    with open(filename, 'w') as f:
        f.write('# Contributors and translators to this repository\n\n')
        f.write('Thank you all for contributing to the project, you are true heroes! 🫶\n\n')
        f.write(f'*Generated on {datetime.date.today()}*\n\n')
        f.write('---\n\n')

        f.write('## Contributors\n\n')
        if contributors:
            for p in deduplicate(contributors):
                entry = generate_markdown(p)
                if entry:
                    f.write(entry)
        else:
            f.write('No contributors found.\n')

        f.write('\n## Translators\n')
        if translators:
            for language, people in sorted(translators.items()):
                f.write('\n')
                f.write(f'### {language}\n\n')
                for p in deduplicate(people):
                    entry = generate_markdown(p)
                    if entry:
                        f.write(entry)
        else:
            f.write('\nNo translators found.\n')

    print(f'{filename} generated successfully.')


def generate_contributors_rst(contributors: list[Person], output_file: str = 'contributors.rst'):
    """Cross-repo, deduplicated contributors list as RST (for the docs site)."""

    sorted_entries = sorted(deduplicate(contributors), key=lambda p: p.name.lower())

    with open(output_file, 'w') as f:
        f.write(':orphan:\n\n')
        f.write('.. _contributors:\n\n')
        f.write('Contributors\n')
        f.write('============\n\n')
        f.write(f'*Generated on {datetime.date.today()}*\n\n')
        f.write(
            'Aggregated code contributors across all wger repositories (backend,\n'
            'react frontend, flutter mobile app, docker, docs). Thank you all\n'
            'for contributing to the project, you are true heroes! 🫶\n\n'
        )
        for p in sorted_entries:
            entry = generate_rst_entry(p)
            if entry:
                f.write(entry)

    print(f'{output_file} generated successfully.')


def generate_translators_rst(
    translators: dict[str, list[Person]], output_file: str = 'translators.rst'
):
    """Cross-repo, deduplicated translators list as RST, grouped by language."""

    with open(output_file, 'w') as f:
        f.write(':orphan:\n\n')
        f.write('.. _translators:\n\n')
        f.write('Translators\n')
        f.write('===========\n\n')
        f.write(f'*Generated on {datetime.date.today()}*\n\n')
        f.write(
            'Thanks to everyone who has helped translate wger into other languages.\n'
            'Contributions are made via `Weblate <https://hosted.weblate.org/engage/wger>`_ \n'
            'and are collected here from all wger repositories.\n\n'
        )
        for language in sorted(translators.keys()):
            f.write(f'{language}\n')
            f.write('-' * len(language) + '\n\n')
            sorted_people = sorted(deduplicate(translators[language]), key=lambda p: p.name.lower())
            for p in sorted_people:
                entry = generate_rst_entry(p)
                if entry:
                    f.write(entry)
            f.write('\n')

    print(f'{output_file} generated successfully.')


if __name__ == '__main__':
    github_token = get_github_token()

    all_contributors: list[Person] = []
    all_translators: dict[str, list[Person]] = {}

    for repo in REPOSITORIES:
        print(f'*** Processing {repo} ***')
        contributors, translators = extract_contributors(repo, github_token)
        generate_authors_file(repo, contributors, translators)

        all_contributors.extend(contributors)
        for lang, people in translators.items():
            all_translators.setdefault(lang, []).extend(people)
        print()

    generate_contributors_rst(all_contributors)
    generate_translators_rst(all_translators)

    print('Done! 🥳')
    print('')

    print('This script can copy the generated files to their correct locations.')
    print('- wger-AUTHORS.md -> ../../AUTHORS.md')
    print('- <repo>-AUTHORS.md -> ../../../<repo>/AUTHORS.md')
    print('- contributors.rst, translators.rst -> ../../../docs/docs/')
    copy_files = input('Copy files? (yes/no): ').strip().lower()

    if copy_files == 'yes':
        print('Copying files...')

        # Copy markdown files
        shutil.copy('wger-AUTHORS.md', '../../AUTHORS.md')
        print('Copied wger-AUTHORS.md to ../../AUTHORS.md')
        for repo in REPOSITORIES:
            # This repo
            if repo == 'wger':
                continue

            # The other ones
            try:
                shutil.copy(f'{repo}-AUTHORS.md', f'../../../{repo}/AUTHORS.md')
                print(f'Copied {repo}-AUTHORS.md to ../../../{repo}/AUTHORS.md')
            except FileNotFoundError as e:
                print(f'Error copying {repo}-AUTHORS.md: {e}')

        # Copy rst files
        for rst_file in ('contributors.rst', 'translators.rst'):
            try:
                shutil.copy(rst_file, f'../../../docs/docs/{rst_file}')
                print(f'Copied {rst_file} to ../../../docs/docs/{rst_file}')
            except FileNotFoundError as e:
                print(f'Error copying {rst_file}: {e}')

        print('Files copied successfully.')
    else:
        print('Files were not copied.')
