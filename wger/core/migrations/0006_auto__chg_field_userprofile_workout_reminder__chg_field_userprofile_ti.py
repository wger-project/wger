# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'UserProfile.workout_reminder'
        db.alter_column(u'core_userprofile', 'workout_reminder', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'UserProfile.timer_pause'
        db.alter_column(u'core_userprofile', 'timer_pause', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'UserProfile.workout_duration'
        db.alter_column(u'core_userprofile', 'workout_duration', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'UserProfile.sleep_hours'
        db.alter_column(u'core_userprofile', 'sleep_hours', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'UserProfile.sport_hours'
        db.alter_column(u'core_userprofile', 'sport_hours', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'UserProfile.freetime_hours'
        db.alter_column(u'core_userprofile', 'freetime_hours', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'UserProfile.height'
        db.alter_column(u'core_userprofile', 'height', self.gf('django.db.models.fields.IntegerField')(max_length=2, null=True))

        # Changing field 'UserProfile.work_hours'
        db.alter_column(u'core_userprofile', 'work_hours', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'UserProfile.age'
        db.alter_column(u'core_userprofile', 'age', self.gf('django.db.models.fields.IntegerField')(max_length=2, null=True))

        # Changing field 'UserProfile.calories'
        db.alter_column(u'core_userprofile', 'calories', self.gf('django.db.models.fields.IntegerField')(null=True))

    def backwards(self, orm):

        # Changing field 'UserProfile.workout_reminder'
        db.alter_column(u'core_userprofile', 'workout_reminder', self.gf('wger.utils.fields.Html5IntegerField')())

        # Changing field 'UserProfile.timer_pause'
        db.alter_column(u'core_userprofile', 'timer_pause', self.gf('wger.utils.fields.Html5IntegerField')())

        # Changing field 'UserProfile.workout_duration'
        db.alter_column(u'core_userprofile', 'workout_duration', self.gf('wger.utils.fields.Html5IntegerField')())

        # Changing field 'UserProfile.sleep_hours'
        db.alter_column(u'core_userprofile', 'sleep_hours', self.gf('wger.utils.fields.Html5IntegerField')(null=True))

        # Changing field 'UserProfile.sport_hours'
        db.alter_column(u'core_userprofile', 'sport_hours', self.gf('wger.utils.fields.Html5IntegerField')(null=True))

        # Changing field 'UserProfile.freetime_hours'
        db.alter_column(u'core_userprofile', 'freetime_hours', self.gf('wger.utils.fields.Html5IntegerField')(null=True))

        # Changing field 'UserProfile.height'
        db.alter_column(u'core_userprofile', 'height', self.gf('wger.utils.fields.Html5IntegerField')(max_length=2, null=True))

        # Changing field 'UserProfile.work_hours'
        db.alter_column(u'core_userprofile', 'work_hours', self.gf('wger.utils.fields.Html5IntegerField')(null=True))

        # Changing field 'UserProfile.age'
        db.alter_column(u'core_userprofile', 'age', self.gf('wger.utils.fields.Html5IntegerField')(max_length=2, null=True))

        # Changing field 'UserProfile.calories'
        db.alter_column(u'core_userprofile', 'calories', self.gf('wger.utils.fields.Html5IntegerField')(null=True))

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
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.daysofweek': {
            'Meta': {'ordering': "['pk']", 'object_name': 'DaysOfWeek'},
            'day_of_week': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'core.language': {
            'Meta': {'ordering': "['full_name']", 'object_name': 'Language'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        u'core.license': {
            'Meta': {'ordering': "['full_name']", 'object_name': 'License'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'})
        },
        u'core.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'age': ('django.db.models.fields.IntegerField', [], {'max_length': '2', 'null': 'True'}),
            'calories': ('django.db.models.fields.IntegerField', [], {'default': '2500', 'null': 'True'}),
            'freetime_hours': ('django.db.models.fields.IntegerField', [], {'default': '8', 'null': 'True'}),
            'freetime_intensity': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '1', 'null': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '1', 'null': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'max_length': '2', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_temporary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_workout_notification': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'notification_language': ('django.db.models.fields.related.ForeignKey', [], {'default': '2', 'to': u"orm['core.Language']"}),
            'show_comments': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_english_ingredients': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'sleep_hours': ('django.db.models.fields.IntegerField', [], {'default': '7', 'null': 'True'}),
            'sport_hours': ('django.db.models.fields.IntegerField', [], {'default': '3', 'null': 'True'}),
            'sport_intensity': ('django.db.models.fields.CharField', [], {'default': "'2'", 'max_length': '1', 'null': 'True'}),
            'timer_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'timer_pause': ('django.db.models.fields.IntegerField', [], {'default': '90'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'}),
            'work_hours': ('django.db.models.fields.IntegerField', [], {'default': '8', 'null': 'True'}),
            'work_intensity': ('django.db.models.fields.CharField', [], {'default': "'1'", 'max_length': '1', 'null': 'True'}),
            'workout_duration': ('django.db.models.fields.IntegerField', [], {'default': '12'}),
            'workout_reminder': ('django.db.models.fields.IntegerField', [], {'default': '14'}),
            'workout_reminder_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['core']