.. _gym:

Gym admnistration
=================

wger has basic support for gym management. There are 3 groups used for the
different administrative roles:

* **general manager:** Can manage (add, edit, delete) the different gyms for the
  installation as well as add gym managers, trainers and member, but is not
  allowed to see the members workout data.
* **gym manager:** Can manage users for a single gym (editing, deactivating,
  adding contracts, etc.).
* **trainer:** Can manage the workouts and other data for the members of a
  single gym.

Except for general managers, administrative users belong to a single gym (the
one they were created in) and can access only those members. This setting cannot
be changed later. The user's gym appears in the in the top right menu (with the
user's name).

.. note:: If the installation is used for a single gym only, you can set the
    default gym in the global configuration options in the gym list. This will
    update all existing users as well as newly registered ones so they belong
    to that gym.

Contracts
---------

It is also possible to manage the member's contracts with the application. A
contract is composed of a base form and optional *type* and *options*. The type
is a single attribute, such as "Student contract" or "Special offer 2016". The
options are basically the same but more than one can be selected at once and
can be used for items that can e.g. be booked in addition to the default
contract such as "Sauna" or "Protein drink flatrate".

The types and the options are added gym-wide in the member overview by the
managers. Once these are saved, they can be used when adding or editing a
contract to a specific user.


Mass emails
-----------


Member management
-----------------





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
