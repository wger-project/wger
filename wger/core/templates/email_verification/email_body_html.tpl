{% load i18n %}
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{% translate 'Email Confirmation' %}</title>
</head>
<body>
<p>{% blocktranslate with username=user.username %}You are almost there, {{ username }}!{% endblocktranslate %}</p>
<br>
<p>{% blocktranslate %}Please click <a href="{{ link }}">here</a> to confirm your email{% endblocktranslate %}</p>
<p>{% blocktranslate with time=expiry|time:"TIME_FORMAT" %}The token expires on {{ time }}{% endblocktranslate %}</p>

<p><i>{% translate 'the wger Team' %}</i></p>
</body>
</html>
