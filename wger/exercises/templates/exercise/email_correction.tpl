A correction has been submitted for the following exercise:
"{{ exercise }}", ID {{ exercise.id }}

User data:
----------
* ID:       {{ user.id }}
* Username: {{ user.username }}
* Email:    {{ user.email }}


Changes to the exercise:
------------------------
* Name:
  - Original: {{ exercise.name }}
  - New:      {{ form_data.name }}

* Category:
  - Original: {{ exercise.exercise_base.category }}
  - New:      {{ form_data.category }}

* Description:
  - Original: {{ exercise.description }}
  - New:      {{ form_data.description }}

* Muscles (primary):
  - Original: {{ exercise.exercise_base.muscles.all|join:", " }}
  - New:      {{ form_data.muscles.all|join:", " }}

* Muscles (secondary):
  - Original: {{ exercise.exercise_base.muscles_secondary.all|join:", " }}
  - New:      {{ form_data.muscles_secondary.all|join:", " }}

* Equipment:
  - Original: {{ exercise.exercise_base.equipment.all|join:", " }}
  - New:      {{ form_data.equipment.all|join:", " }}

* License:
  - Original: {{ exercise.license }}
  - New:      {{ form_data.license }}

* Author:
  - Original: {{ exercise.license_author }}
  - New:      {{ form_data.license_author }}