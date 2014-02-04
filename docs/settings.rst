Settings
========

You can configure some of the application behaviour with the ``WGER_SETTINGS``
dictionary in your settings file. Currently the following options are supported:

* **USE_RECAPTCHA**: Default ``False``. Controls whether a captcha challenge
  will be presented when new users register.


.. note::
  If you want to override a default setting, don't overwrite all the dictionary
  but only the keys you need, e.g. ``WGER_SETTINGS['foo'] = 'bar'``. This avoids
  problems when new keys are added in the global settings.

