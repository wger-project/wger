{% spaceless %}{% load i18n %}

{% blocktrans %}Your last weight entry is from {{date}} ({{days}} days ago).
Please click the link to access the application and enter a new one.{% endblocktrans %}

{% endspaceless %}

{% blocktrans %}You will regularly receive such reminders till you enter your current weight.{% endblocktrans %}
{% blocktrans %}If you don't want to ever receive email reminders, deactivate the
option in your settings.{% endblocktrans %}

— {% blocktrans %}The {{ site }} team{% endblocktrans %}


* https://{{site}}{% url 'weight:overview' user.username %}
* https://{{site}}{% url 'weight:add' %}
* https://{{site}}{% url 'core:user:preferences' %}
