.. _gym:

Gym admnistration
=================

wger has support for gym and member management, allowing e.g. trainers to follow
the progress of their athletes and for the gym managers to keep track of the
member's contracts.

It is possible to manage a single or different ones with one instance of wger.
If the installation is used for a single gym only, you can set the
default gym in the global configuration options in the gym list. This will
update all existing users as well as newly registered ones so they belong
to that gym.


There are 3 groups used for the different administrative roles:

* **general manager:** Can manage (add, edit, delete) the different gyms for the
  installation as well as add gym managers, trainers and member, but is not
  allowed to see the members' workout data.
* **gym manager:** Can manage users for a single gym (editing, deactivating,
  adding contracts, etc.).
* **trainer:** Can manage the workouts and other data for the members of a
  single gym.

These roles are not mutually exclusive, if your workflow demands it, you can
combine all three roles into one account.

Except for general managers, administrative users belong to a single gym (the
one they were created in) and can access only those members. This setting cannot
be changed later. The user's gym appears in the top right menu.


Member management
-----------------
You can add members to a gym by clicking the *Add member* button at the top of
the member overview. After filling in the form, a password will be generated
for the user. You should save this and give it to the user, as it is not possible
to retrieve it later. Alternatively you can just instruct the new members to
use the reset password links when logging in for the first time.

An export of all gym members is available as well from the "actions" button on
the gym detail table. This provides a CSV file that can be imported into a
spreadsheet program for further processing.

Trainers can click on a user and access an overview of the user's workouts,
body weights, nutrition plans, etc. When clicking on the "log in as this user",
the trainer can assume the identity of the user to create new workouts for
example.

Individual members can be deactivated by clicking on the "actions" button on
the top of the member's detail table. Deactivated users can't log in, but are
not deleted from the system and can be reactivated at any time in the future.
If you wish to completely delete a user from the system, use the "delete"
option but keep in mind that this action cannot be undone.


Notes and documents
-------------------
Trainers can add notes and upload documents related to individual members. A
note is a free text, while a document can be any file. This information can
be used to save information on specific injuries or other important notes
related to the member. Note that these entries are not accessible by the
members themselves, but only by the trainers.


Contracts
---------

It is also possible to manage the members' contracts with the application. A
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
It is possible to send an email to all members of a gym. At the moment it is
not possible to filter this list or send it only to members that fulfill a
specific criterion.

To send this, go to the gym's overview and click "Add" on the Email actions
button. After filling in the subject and the body you need to accept the
preview, in order to make sure that the text you wrote is indeed the one
you intend to send. After submitting the form, the emails will be sent in
batches (how exactly depends on how you configured the different cron jobs
needed to run the application).


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

Gym name in header
~~~~~~~~~~~~~~~~~~
A checkbox to control whether the gym's name will appear in the header instead
of the application's name for all logged in users of this gym. This applies to
members, trainers and managers.
