Adding new languages
====================

After adding new translations to this locale folder, they have to be activated
in django and in the application itself.

* **django:** Add an entry to ``LANGUAGES`` in ``settings_global.py``
* **wger:** Add the new language in the language admin page and set the
  visibility of excercises and ingredients
* **fixtures:** After having added the language in the admin module, export
  the database, filter it with the ``filter-fixtures.py`` script in
  ``extras/scripts`` and copy ``language_config.json`` to the fixtures folder
  in the config app.
* **flag icon:** Add an appropriate flag icon in SVG format in ``images/icons/flag-NAME.svg``
  in the static folder of the core application
