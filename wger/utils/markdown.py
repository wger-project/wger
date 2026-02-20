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
# Third party
import nh3
from markdown_it import MarkdownIt


def render_markdown(text):
    """
    Renders markdown text to HTML and sanitizes it to allow only basic markup.
    """
    if not text:
        return ''

    # Render Markdown to HTML
    md = MarkdownIt('commonmark', {'breaks': True, 'html': True})
    raw_html = md.render(text)

    # Sanitize HTML
    ALLOWED_TAGS = {'b', 'strong', 'i', 'em', 'ul', 'ol', 'li', 'p'}

    clean_html = nh3.clean(raw_html, tags=ALLOWED_TAGS, attributes={})

    return clean_html


def sanitize_html(text):
    """
    Directly sanitizes HTML (for legacy fields or non-markdown inputs)
    """
    if not text:
        return ''

    ALLOWED_TAGS = {'b', 'strong', 'i', 'em', 'ul', 'ol', 'li', 'p'}
    return nh3.clean(text, tags=ALLOWED_TAGS, attributes={})
