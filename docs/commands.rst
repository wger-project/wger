Management commands
===================

wger also implements a series of django commands that perform different
management functions that are sometimes needed. Call them with
``python manage.py command_name``:

**download-exercise-images**
  synchronizes the exercise images from wger.de to the local installation. Read
  its help text as it could save the wrong image to the wrong exercise should
  different IDs match.

**extract-i18n**
  extract strings from the database that have to be inserted manually in the PO
  file when translating. These include e.g. exercise categories.

**clear-cache**
  clears different application caches. Might be needed after some updates or
  just useful while testing. Please note that you must select what caches to
  clear.

**submitted-exercises**
  simply prints a list of user submitted exercises


Cron
----

The following commands are built to be called regularly, via a cronjob or
similar

**delete-temp-users**
  deletes all guest users older than 1 week. At the moment this value can't be
  configured

**email-reminders**
  sends out email reminders for user that need to create a new workout.

**inactive-members**
  Sends email for gym members that have not been to the gym for a specified
  amount of weeks.
  
  
