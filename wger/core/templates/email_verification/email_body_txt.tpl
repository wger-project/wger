{% load i18n %}

{% blocktranslate with username=user.username %}You are almost there, {{ username }}!{% endblocktranslate %}
{% blocktranslate %}Please click the following link to confirm your email: {{ link }}{% endblocktranslate %}
{% blocktranslate with time=expiry|time:"TIME_FORMAT" %}The token expires on {{ time }}{% endblocktranslate %}


{% translate 'the wger Team' %}
