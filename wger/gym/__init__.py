import wger.gym.signals


# TODO: django1.7
# http://stackoverflow.com/questions/2719038/where-should-signal-handlers-liv

# When you upgrade to Django 1.7, you would remove the "import .signals" from
# your __ init__.py and add an yourapp/apps.py like the following:
#
# from django.apps import AppConfig
#
# class ReportsConfig(AppConfig):
#    name = 'reports'
#    verbose_name = "Reports"
#
#    def ready(self):
#        import signals
