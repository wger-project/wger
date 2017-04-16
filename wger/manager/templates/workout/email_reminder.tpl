{% spaceless %}{% load i18n %}
{% if expired %}
    {% blocktrans %}Your current workout '{{workout}}' expired {{days}} days ago.{% endblocktrans %}
{% else %}
    {% blocktrans %}Your current workout '{{workout}}' is about to expire in {{days}} days.{% endblocktrans %}
{% endif %}
{% endspaceless %}

{% blocktrans %}You will regularly receive such reminders till you add a new workout.
Alternatively you can add workouts to a loop schedule, such schedules
never produce reminders.{% endblocktrans %}
{% blocktrans %}If you don't want to ever receive email reminders, deactivate the
option in your settings.{% endblocktrans %}

— {% blocktrans %}The {{ site }} team{% endblocktrans %}


* https://{{site}}{{workout.get_absolute_url}}
* https://{{site}}{% url 'manager:workout:add' %}
* https://{{site}}{% url 'core:user:preferences' %}
