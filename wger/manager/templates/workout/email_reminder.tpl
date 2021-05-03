{% spaceless %}{% load i18n %}
{% if expired %}
    {% blocktranslate %}Your current workout '{{workout}}' expired {{days}} days ago.{% endblocktranslate %}
{% else %}
    {% blocktranslate %}Your current workout '{{workout}}' is about to expire in {{days}} days.{% endblocktranslate %}
{% endif %}
{% endspaceless %}

{% blocktranslate %}You will regularly receive such reminders till you add a new workout.
Alternatively you can add workouts to a loop schedule, such schedules
never produce reminders.{% endblocktranslate %}
{% blocktranslate %}If you don't want to ever receive email reminders, deactivate the
option in your settings.{% endblocktranslate %}

— {% blocktranslate %}The {{ site }} team{% endblocktranslate %}


* https://{{site}}{{workout.get_absolute_url}}
* https://{{site}}{% url 'manager:workout:add' %}
* https://{{site}}{% url 'core:user:preferences' %}
