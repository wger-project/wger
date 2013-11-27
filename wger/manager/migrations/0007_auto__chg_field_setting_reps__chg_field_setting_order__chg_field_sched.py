# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Setting.reps'
        db.alter_column(u'manager_setting', 'reps', self.gf('wger.utils.fields.Html5IntegerField')())

        # Changing field 'Setting.order'
        db.alter_column(u'manager_setting', 'order', self.gf('wger.utils.fields.Html5IntegerField')())

        # Changing field 'Schedule.start_date'
        db.alter_column(u'manager_schedule', 'start_date', self.gf('wger.utils.fields.Html5DateField')())

        # Changing field 'Set.order'
        db.alter_column(u'manager_set', 'order', self.gf('wger.utils.fields.Html5IntegerField')(max_length=1, null=True))

        # Changing field 'Set.sets'
        db.alter_column(u'manager_set', 'sets', self.gf('wger.utils.fields.Html5IntegerField')())

        # Changing field 'UserProfile.age'
        db.alter_column(u'manager_userprofile', 'age', self.gf('wger.utils.fields.Html5IntegerField')(max_length=2, null=True))

        # Changing field 'UserProfile.calories'
        db.alter_column(u'manager_userprofile', 'calories', self.gf('wger.utils.fields.Html5IntegerField')(null=True))

        # Changing field 'UserProfile.height'
        db.alter_column(u'manager_userprofile', 'height', self.gf('wger.utils.fields.Html5IntegerField')(max_length=2, null=True))

        # Changing field 'UserProfile.sport_hours'
        db.alter_column(u'manager_userprofile', 'sport_hours', self.gf('wger.utils.fields.Html5IntegerField')(null=True))

        # Changing field 'UserProfile.sleep_hours'
        db.alter_column(u'manager_userprofile', 'sleep_hours', self.gf('wger.utils.fields.Html5IntegerField')(null=True))

        # Changing field 'UserProfile.freetime_hours'
        db.alter_column(u'manager_userprofile', 'freetime_hours', self.gf('wger.utils.fields.Html5IntegerField')(null=True))

        # Changing field 'UserProfile.work_hours'
        db.alter_column(u'manager_userprofile', 'work_hours', self.gf('wger.utils.fields.Html5IntegerField')(null=True))

        # Changing field 'WorkoutLog.weight'
        db.alter_column(u'manager_workoutlog', 'weight', self.gf('wger.utils.fields.Html5DecimalField')(max_digits=5, decimal_places=2))

        # Changing field 'WorkoutLog.reps'
        db.alter_column(u'manager_workoutlog', 'reps', self.gf('wger.utils.fields.Html5IntegerField')())

        # Changing field 'WorkoutLog.date'
        db.alter_column(u'manager_workoutlog', 'date', self.gf('wger.utils.fields.Html5DateField')())

        # Changing field 'ScheduleStep.duration'
        db.alter_column(u'manager_schedulestep', 'duration', self.gf('wger.utils.fields.Html5IntegerField')(max_length=1))

    def backwards(self, orm):

        # Changing field 'Setting.reps'
        db.alter_column(u'manager_setting', 'reps', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Setting.order'
        db.alter_column(u'manager_setting', 'order', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Schedule.start_date'
        db.alter_column(u'manager_schedule', 'start_date', self.gf('django.db.models.fields.DateField')())

        # Changing field 'Set.order'
        db.alter_column(u'manager_set', 'order', self.gf('django.db.models.fields.IntegerField')(max_length=1, null=True))

        # Changing field 'Set.sets'
        db.alter_column(u'manager_set', 'sets', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'UserProfile.age'
        db.alter_column(u'manager_userprofile', 'age', self.gf('django.db.models.fields.IntegerField')(max_length=2, null=True))

        # Changing field 'UserProfile.calories'
        db.alter_column(u'manager_userprofile', 'calories', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'UserProfile.height'
        db.alter_column(u'manager_userprofile', 'height', self.gf('django.db.models.fields.IntegerField')(max_length=2, null=True))

        # Changing field 'UserProfile.sport_hours'
        db.alter_column(u'manager_userprofile', 'sport_hours', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'UserProfile.sleep_hours'
        db.alter_column(u'manager_userprofile', 'sleep_hours', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'UserProfile.freetime_hours'
        db.alter_column(u'manager_userprofile', 'freetime_hours', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'UserProfile.work_hours'
        db.alter_column(u'manager_userprofile', 'work_hours', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'WorkoutLog.weight'
        db.alter_column(u'manager_workoutlog', 'weight', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2))

        # Changing field 'WorkoutLog.reps'
        db.alter_column(u'manager_workoutlog', 'reps', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'WorkoutLog.date'
        db.alter_column(u'manager_workoutlog', 'date', self.gf('django.db.models.fields.DateField')())

        # Changing field 'ScheduleStep.duration'
        db.alter_column(u'manager_schedulestep', 'duration', self.gf('django.db.models.fields.IntegerField')(max_length=1))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'exercises.equipment': {
            'Meta': {'ordering': "['name']", 'object_name': 'Equipment'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'exercises.exercise': {
            'Meta': {'ordering': "['name']", 'object_name': 'Exercise'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exercises.ExerciseCategory']"}),
            'creation_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000'}),
            'equipment': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['exercises.Equipment']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exercises.Language']"}),
            'muscles': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['exercises.Muscle']", 'symmetrical': 'False'}),
            'muscles_secondary': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'secondary_muscles'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['exercises.Muscle']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '2'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'exercises.exercisecategory': {
            'Meta': {'ordering': "['name']", 'object_name': 'ExerciseCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'exercises.language': {
            'Meta': {'object_name': 'Language'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        u'exercises.muscle': {
            'Meta': {'ordering': "['name']", 'object_name': 'Muscle'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_front': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'manager.day': {
            'Meta': {'object_name': 'Day'},
            'day': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['manager.DaysOfWeek']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'training': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['manager.Workout']"})
        },
        u'manager.daysofweek': {
            'Meta': {'ordering': "['pk']", 'object_name': 'DaysOfWeek'},
            'day_of_week': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'manager.schedule': {
            'Meta': {'object_name': 'Schedule'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_loop': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'start_date': ('wger.utils.fields.Html5DateField', [], {'default': 'datetime.date.today'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'manager.schedulestep': {
            'Meta': {'ordering': "['order']", 'object_name': 'ScheduleStep'},
            'duration': ('wger.utils.fields.Html5IntegerField', [], {'default': '4', 'max_length': '1'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '1'}),
            'schedule': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['manager.Schedule']"}),
            'workout': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['manager.Workout']"})
        },
        u'manager.set': {
            'Meta': {'ordering': "['order']", 'object_name': 'Set'},
            'exerciseday': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['manager.Day']"}),
            'exercises': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['exercises.Exercise']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('wger.utils.fields.Html5IntegerField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'sets': ('wger.utils.fields.Html5IntegerField', [], {'default': '4'})
        },
        u'manager.setting': {
            'Meta': {'ordering': "['order', 'id']", 'object_name': 'Setting'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exercises.Exercise']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('wger.utils.fields.Html5IntegerField', [], {'blank': 'True'}),
            'reps': ('wger.utils.fields.Html5IntegerField', [], {}),
            'set': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['manager.Set']"})
        },
        u'manager.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'age': ('wger.utils.fields.Html5IntegerField', [], {'max_length': '2', 'null': 'True'}),
            'calories': ('wger.utils.fields.Html5IntegerField', [], {'default': '2500', 'null': 'True'}),
            'freetime_hours': ('wger.utils.fields.Html5IntegerField', [], {'default': '8', 'null': 'True'}),
            'freetime_intensity': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '1', 'null': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '1', 'null': 'True'}),
            'height': ('wger.utils.fields.Html5IntegerField', [], {'max_length': '2', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_temporary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_english_ingredients': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sleep_hours': ('wger.utils.fields.Html5IntegerField', [], {'default': '7', 'null': 'True'}),
            'sport_hours': ('wger.utils.fields.Html5IntegerField', [], {'default': '3', 'null': 'True'}),
            'sport_intensity': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '1', 'null': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'work_hours': ('wger.utils.fields.Html5IntegerField', [], {'default': '8', 'null': 'True'}),
            'work_intensity': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '1', 'null': 'True'})
        },
        u'manager.workout': {
            'Meta': {'ordering': "['-creation_date']", 'object_name': 'Workout'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'manager.workoutlog': {
            'Meta': {'ordering': "['date', 'reps']", 'object_name': 'WorkoutLog'},
            'date': ('wger.utils.fields.Html5DateField', [], {}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['exercises.Exercise']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reps': ('wger.utils.fields.Html5IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'weight': ('wger.utils.fields.Html5DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'workout': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['manager.Workout']"})
        }
    }

    complete_apps = ['manager']