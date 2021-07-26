{% spaceless %}{% load i18n %}

{% blocktranslate %}Your last weight entry is from {{date}} ({{days}} days ago).
Please click the link to access the application and enter a new one.{% endblocktranslate %}

{% endspaceless %}

{% blocktranslate %}You will regularly receive such reminders till you enter your current weight.{% endblocktranslate %}
{% blocktranslate %}If you don't want to ever receive email reminders, deactivate the
option in your settings.{% endblocktranslate %}

— {% blocktranslate %}The {{ site }} team{% endblocktranslate %}


* https://{{site}}{% url 'weight:overview' %}
* https://{{site}}{% url 'weight:add' %}
* https://{{site}}{% url 'core:user:preferences' %}
