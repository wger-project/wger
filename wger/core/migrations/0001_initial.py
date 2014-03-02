# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    depends_on = (
        ('manager', '0014_auto__chg_field_workoutsession_date__add_field_userprofile_timer_activ'),
        ('weight', '0002_auto__add_unique_weightentry_user_creation_date'),
        ('exercises', '0014_auto__del_field_exercise_user_tmp__add_field_exercise_user'),
        ('nutrition', '0008_auto__add_field_nutritionplan_has_goal_calories__chg_field_ingredient_'),
        ('config', '0002_language_config'),
    )

    def forwards(self, orm):
        pass

    def backwards(self, orm):
        pass

    models = {
        
    }

    complete_apps = ['core']