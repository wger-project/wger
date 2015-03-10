.. _gym:

Gym admnistration
=================

wger has basic support for gym management. There are 3 groups used for the
different administrative roles:

* **general manager:** Can manage (add, edit, delete) the different gyms for the
  installation but is not allowed to access or add members.
* **gym manager:** Can manage users for a single gym.
* **trainer:** Can manage the workouts and other data for the members of a
  single gym.

If the installation is used for a single gym only, you can set the default gym.
This will update all existing users as well as newly registered ones so they
belong to that gym


Configuration
-------------

Inactive members
~~~~~~~~~~~~~~~~
The idea behind the inactive members is that trainers want to know which users
have not visited the gym for longer than X weeks and e.g. contact them.
'Inactive' means here that they don't have any logs in the time period.

This can be configured in the following ways:

**number of weeks**
  The value in weeks after which users are considered inactive (default is 8).
  This applies to the whole gym and can be deactivated by entering a 0.

**trainer configuration**
  Each trainer can opt-out of receiving such emails

**user configuration**
  Individual users can be opt-out of being included in the reminder emails if
  they don't want to use the log or any other reason.
