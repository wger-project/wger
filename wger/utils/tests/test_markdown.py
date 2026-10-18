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

# Standard Library
import unittest

# wger
from wger.utils.markdown import (
    render_markdown,
    sanitize_html,
)


class TestMarkdown(unittest.TestCase):
    """
    Test the markdown rendering and HTML sanitization utilities.
    Allowed tags: a (href only), b, strong, i, em, ul, ol, li, p
    """

    def test_render_markdown_basic(self):
        """
        Test that basic markdown syntax is rendered to HTML.
        """
        # Bold and Italic
        text = 'I like **osaka** and eating *sata-andagi*.'
        output = render_markdown(text)

        self.assertTrue('<strong>osaka</strong>' in output or '<b>osaka</b>' in output)
        self.assertTrue('<em>sata-andagi</em>' in output or '<i>sata-andagi</i>' in output)
        self.assertIn('<p>', output)

    def test_render_markdown_lists(self):
        """
        Test that lists are rendered correctly.
        """
        text = '- Item 1\n- Item 2'
        output = render_markdown(text)

        self.assertIn('<ul>', output)
        self.assertIn('<li>Item 1</li>', output)
        self.assertIn('<li>Item 2</li>', output)

    def test_render_markdown_strips_disallowed_tags(self):
        """
        Test that valid markdown generating disallowed tags (e.g. headings, images)
        results in the tag being stripped.
        """
        # Heading 1 (<h1> is not allowed)
        text = '# Big Title'
        output = render_markdown(text)

        self.assertNotIn('<h1>', output)
        self.assertIn('Big Title', output)  # Content remains, tag is removed

        # Image (<img> is not allowed)
        text = '![Alt text](http://example.com/img.jpg)'
        output = render_markdown(text)

        self.assertNotIn('<img', output)

    def test_render_markdown_xss_prevention(self):
        """
        Test that script tags and dangerous attributes are removed.
        """
        # Script injection via Markdown/HTML mix
        text = "Hello <script>alert('XSS')</script>"
        output = render_markdown(text)

        self.assertNotIn('<script>', output)
        self.assertNotIn('alert', output)

        # Dangerous attributes
        text = '<p onclick="maliciousCode()">Click me</p>'
        output = render_markdown(text)

        self.assertNotIn('onclick', output)
        self.assertIn('<p>Click me</p>', output)

    def test_sanitize_html_legacy(self):
        """
        Test the direct HTML sanitizer used for legacy fields.
        """
        html = '<b>Bold</b> and <u>underline</u>'
        output = sanitize_html(html)

        self.assertIn('<b>Bold</b>', output)
        self.assertNotIn('<u>', output)  # Not in the allowed list
        self.assertIn('underline', output)  # Content usually preserved

    def test_links_are_kept(self):
        """
        Test that markdown and HTML links keep their href and get a safe rel.
        """
        output = render_markdown('Demo: [video](https://example.com/demo)')
        self.assertIn(
            '<a href="https://example.com/demo" rel="noopener noreferrer">video</a>', output
        )

        output = sanitize_html('<a href="https://example.com/demo">video</a>')
        self.assertIn(
            '<a href="https://example.com/demo" rel="noopener noreferrer">video</a>', output
        )

    def test_links_unsafe_parts_removed(self):
        """
        Test that script URLs and attributes other than href are removed from links.
        """
        output = render_markdown('[click](javascript:alert(1))')
        self.assertNotIn('<a', output)  # markdown-it refuses to link it

        output = render_markdown('<a href="javascript:alert(1)">click</a>')
        self.assertNotIn('javascript', output)
        self.assertIn('click', output)

        output = sanitize_html('<a href="data:text/html,hi" onclick="x()" style="color:red">hi</a>')
        self.assertNotIn('data:', output)
        self.assertNotIn('onclick', output)
        self.assertNotIn('style', output)
        self.assertIn('hi', output)

        output = sanitize_html('<a href="https://example.com" target="_blank" rel="opener">x</a>')
        self.assertNotIn('target', output)
        self.assertIn('rel="noopener noreferrer"', output)

    def test_empty_inputs(self):
        """
        Test handling of None or empty strings.
        """
        self.assertEqual(render_markdown(None), '')
        self.assertEqual(render_markdown(''), '')
        self.assertEqual(sanitize_html(None), '')
        self.assertEqual(sanitize_html(''), '')


if __name__ == '__main__':
    unittest.main()
