# Standard Library
import datetime
import json
import os
import re
import shutil
from getpass import getpass
from pathlib import Path

# Third Party
import requests

# /// script
# dependencies = [
#   "requests",
# ]
# ///

ORGANIZATION = 'wger-project'
REPOSITORIES = ['wger', 'flutter', 'react', 'docker', 'docs']
COMMITS_PER_PAGE = 100
CACHE_DIR = Path('commits_cache')


def get_github_token():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        token = getpass('Enter your GitHub token: ')

    return token


def fetch_commits_from_github(repo_name, github_token):
    repo_cache_dir = CACHE_DIR / repo_name
    repo_cache_dir.mkdir(parents=True, exist_ok=True)

    url = f'https://api.github.com/repos/{ORGANIZATION}/{repo_name}/commits'
    headers = {'Authorization': f'token {github_token}'} if github_token else {}
    commits = []

    # Get total commit count
    try:
        response = requests.get(url, headers=headers, params={'per_page': COMMITS_PER_PAGE})
        response.raise_for_status()
        link_header = response.headers.get('Link')
        if link_header:
            links = link_header.split(', ')
            for link in links:
                if 'rel="last"' in link:
                    match = re.search(r'[?&]page=(\d+)', link)
                    if match:
                        total_pages = int(match.group(1))
                        break
            else:
                total_pages = 1  # if the last page is not found, assume one page.
        else:
            total_pages = 1
    except requests.exceptions.RequestException as e:
        print(f'Error getting total commits: {e}')
        return []

    # print(f"Total pages: {total_pages}")
    for page in range(1, total_pages + 1):
        # page += 1
        cache_file = repo_cache_dir / f'page_{page}.json'

        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
            commits.extend(data)
            print(f'Loaded cached page {page}')
            continue

        try:
            response = requests.get(
                url, headers=headers, params={'page': page, 'per_page': COMMITS_PER_PAGE}
            )
            response.raise_for_status()
            data = response.json()

            if not data:
                break

            print(f'Fetching commits from API for page {page}')

            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=4)

            commits.extend(data)
        except requests.exceptions.RequestException as e:
            print(f'Error fetching commits: {e}')
            break

        break

    return commits


def extract_contributors(repo_name, github_token):
    """Retrieves contributors and translators from the GitHub API."""

    contributors = {}
    translators = {}

    commits = fetch_commits_from_github(repo_name, github_token)

    for commit in commits:
        commit_message = commit['commit']['message']

        # Author is null if the commit was done by weblate and the translator is not a GitHub user
        author = commit.get('author', {})
        author_username = author.get('login', '') if author else ''
        author_name = commit['commit']['author']['name']
        author_email = commit['commit']['author']['email']

        if 'dependabot' in author_name:
            continue

        if 'github-actions' in author_name:
            continue

        if '@' in author_name:
            author_name = f'<{author_name.replace("@", " [at] ")}>'

        if 'Translated using Weblate' in commit_message:
            language_match = re.search(r'Translated using Weblate \((.+)\)', commit_message)
            if language_match:
                language = language_match.group(1)
                if language not in translators:
                    translators[language] = {}

                translators[language][author_email] = {
                    'email': author_email,
                    'name': author_name,
                    'username': author_username,
                }
        else:
            contributors[author_email] = {
                'email': author_email,
                'username': author_username,
                'name': author_name,
            }
    return contributors, translators


def generate_markdown(data: dict) -> str | None:
    """Generate the markdown for a single contributor or translator."""

    profile = f'https://github.com/{data.get("username", "")}'
    entry = f'{data["name"]} - [{profile}]({profile})' if data['username'] else data['name']

    if entry == '':
        return None

    return f'- {entry}\n'


def generate_authors_file(
    repo_name, contributors: dict, translators: dict, output_file='AUTHORS.md'
):
    """Generates a Markdown file with contributors and translators."""
    filename = f'{repo_name}-{output_file}'

    with open(filename, 'w') as f:
        f.write('# Contributors and translators to this repository\n\n')
        f.write('Thank you all for contributing to the project, you are true heroes! 🫶\n\n')
        f.write(f'*Generated on {datetime.date.today()}*\n\n')
        f.write('---\n\n')

        f.write('## Contributors\n\n')
        if contributors:
            for author_email, data in contributors.items():
                entry = generate_markdown(data)
                if entry:
                    f.write(entry)
        else:
            f.write('No contributors found.\n')

        f.write('\n## Translators\n')
        if translators:
            for language, translator_data in sorted(translators.items()):
                f.write('\n')
                f.write(f'### {language}\n\n')
                for author_email, data in translator_data.items():
                    entry = generate_markdown(data)
                    if entry:
                        f.write(entry)
        else:
            f.write('\nNo translators found.\n')

    print(f'{filename} generated successfully.')


if __name__ == '__main__':
    github_token = get_github_token()

    for repo in REPOSITORIES:
        print(f'*** Processing {repo} ***')
        generate_authors_file(repo, *extract_contributors(repo, github_token))
        print(f'')

    print('Done! 🥳')
    print('')

    print('This script can copy the generated AUTHORS.md files to their correct locations.')
    print('- wger-AUTHORS.md -> ../../AUTHORS.md')
    print('- <repo>-AUTHORS.md -> ../../../<repo>/AUTHORS.md')
    copy_files = input('Copy files? (yes/no): ').strip().lower()

    if copy_files == 'yes':
        print('Copying files...')
        shutil.copy('wger-AUTHORS.md', '../../AUTHORS.md')
        print('Copied wger-AUTHORS.md to ../../AUTHORS.md')
        for repo in REPOSITORIES:
            if repo == 'wger':
                continue
            try:
                shutil.copy(f'{repo}-AUTHORS.md', f'../../../{repo}/AUTHORS.md')
                print(f'Copied {repo}-AUTHORS.md to ../../../{repo}/AUTHORS.md')
            except FileNotFoundError as e:
                print(f'Error copying {repo}-AUTHORS.md: {e}')
        print('Files copied successfully.')
    else:
        print('Files were not copied.')
