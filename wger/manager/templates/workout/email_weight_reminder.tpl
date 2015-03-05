{% spaceless %}{% load i18n %}

{% blocktrans %}Your last weight entry is from {{day}}. Please click the link above to access wger and update this information. {% endblocktrans %}

{% endspaceless %}

{% blocktrans %}You will regularly receive such reminders till you entry your weight.
If you don't want to ever receive email
reminders, deactivate the option in your settings.{% endblocktrans %}

{% trans "the wger.de team" %}


* http://{{site}}{% url 'weight:overview' %}
* http://{{site}}{% url 'core:user:preferences' %}