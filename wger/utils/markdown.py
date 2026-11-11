# -*- coding: utf-8 -*-

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Third Party
import nh3
from markdown_it import MarkdownIt


ALLOWED_TAGS = {'a', 'b', 'strong', 'i', 'em', 'ul', 'ol', 'li', 'p'}

# Links keep only their target, and only for web and mail addresses
# (no javascript: or data: URLs); nh3 adds rel="noopener noreferrer".
ALLOWED_ATTRIBUTES = {'a': {'href'}}
ALLOWED_URL_SCHEMES = {'http', 'https', 'mailto'}


def _clean(html):
    return nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_URL_SCHEMES,
    )


def render_markdown(text):
    """
    Renders markdown text to HTML and sanitizes it to allow only basic markup.
    """
    if not text:
        return ''

    # Render Markdown to HTML
    md = MarkdownIt('commonmark', {'breaks': True, 'html': True})
    raw_html = md.render(text)

    return _clean(raw_html)


def sanitize_html(text):
    """
    Directly sanitizes HTML (for legacy fields or non-markdown inputs)
    """
    if not text:
        return ''

    return _clean(text)
