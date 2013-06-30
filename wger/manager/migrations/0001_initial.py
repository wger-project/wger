# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TrainingSchedule'
        db.create_table('manager_trainingschedule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('creation_date', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(max_length=100, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
        ))
        db.send_create_signal('manager', ['TrainingSchedule'])

        # Adding model 'DaysOfWeek'
        db.create_table('manager_daysofweek', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('day_of_week', self.gf('django.db.models.fields.CharField')(max_length=9)),
        ))
        db.send_create_signal('manager', ['DaysOfWeek'])

        # Adding model 'Day'
        db.create_table('manager_day', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('training', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['manager.TrainingSchedule'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal('manager', ['Day'])

        # Adding M2M table for field day on 'Day'
        db.create_table('manager_day_day', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('day', models.ForeignKey(orm['manager.day'], null=False)),
            ('daysofweek', models.ForeignKey(orm['manager.daysofweek'], null=False))
        ))
        db.create_unique('manager_day_day', ['day_id', 'daysofweek_id'])

        # Adding model 'Set'
        db.create_table('manager_set', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exerciseday', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['manager.Day'])),
            ('order', self.gf('django.db.models.fields.IntegerField')(max_length=1, null=True, blank=True)),
            ('sets', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('manager', ['Set'])

        # Adding M2M table for field exercises on 'Set'
        db.create_table('manager_set_exercises', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('set', models.ForeignKey(orm['manager.set'], null=False)),
            ('exercise', models.ForeignKey(orm['exercises.exercise'], null=False))
        ))
        db.create_unique('manager_set_exercises', ['set_id', 'exercise_id'])

        # Adding model 'Setting'
        db.create_table('manager_setting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('set', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['manager.Set'])),
            ('exercise', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exercises.Exercise'])),
            ('reps', self.gf('django.db.models.fields.IntegerField')()),
            ('order', self.gf('django.db.models.fields.IntegerField')(blank=True)),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('manager', ['Setting'])

        # Adding model 'WorkoutLog'
        db.create_table('manager_workoutlog', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('exercise', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exercises.Exercise'])),
            ('workout', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['manager.TrainingSchedule'])),
            ('reps', self.gf('django.db.models.fields.IntegerField')()),
            ('weight', self.gf('django.db.models.fields.DecimalField')(max_digits=5, decimal_places=2)),
            ('date', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal('manager', ['WorkoutLog'])

        # Adding model 'UserProfile'
        db.create_table('manager_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('is_temporary', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_comments', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('show_english_ingredients', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('manager', ['UserProfile'])


    def backwards(self, orm):
        # Deleting model 'TrainingSchedule'
        db.delete_table('manager_trainingschedule')

        # Deleting model 'DaysOfWeek'
        db.delete_table('manager_daysofweek')

        # Deleting model 'Day'
        db.delete_table('manager_day')

        # Removing M2M table for field day on 'Day'
        db.delete_table('manager_day_day')

        # Deleting model 'Set'
        db.delete_table('manager_set')

        # Removing M2M table for field exercises on 'Set'
        db.delete_table('manager_set_exercises')

        # Deleting model 'Setting'
        db.delete_table('manager_setting')

        # Deleting model 'WorkoutLog'
        db.delete_table('manager_workoutlog')

        # Deleting model 'UserProfile'
        db.delete_table('manager_userprofile')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'exercises.exercise': {
            'Meta': {'ordering': "['name']", 'object_name': 'Exercise'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['exercises.ExerciseCategory']"}),
            'description': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'muscles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['exercises.Muscle']", 'symmetrical': 'False'}),
            'muscles_secondary': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'secondary_muscles'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['exercises.Muscle']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'exercises.exercisecategory': {
            'Meta': {'ordering': "['name']", 'object_name': 'ExerciseCategory'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['exercises.Language']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'exercises.language': {
            'Meta': {'object_name': 'Language'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'exercises.muscle': {
            'Meta': {'ordering': "['name']", 'object_name': 'Muscle'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_front': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'manager.day': {
            'Meta': {'object_name': 'Day'},
            'day': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['manager.DaysOfWeek']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'training': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manager.TrainingSchedule']"})
        },
        'manager.daysofweek': {
            'Meta': {'object_name': 'DaysOfWeek'},
            'day_of_week': ('django.db.models.fields.CharField', [], {'max_length': '9'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'manager.set': {
            'Meta': {'ordering': "['order']", 'object_name': 'Set'},
            'exerciseday': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manager.Day']"}),
            'exercises': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['exercises.Exercise']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'sets': ('django.db.models.fields.IntegerField', [], {})
        },
        'manager.setting': {
            'Meta': {'ordering': "['order', 'id']", 'object_name': 'Setting'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['exercises.Exercise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'order': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'reps': ('django.db.models.fields.IntegerField', [], {}),
            'set': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manager.Set']"})
        },
        'manager.trainingschedule': {
            'Meta': {'ordering': "['-creation_date']", 'object_name': 'TrainingSchedule'},
            'comment': ('django.db.models.fields.TextField', [], {'max_length': '100', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'manager.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_temporary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_comments': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_english_ingredients': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        },
        'manager.workoutlog': {
            'Meta': {'ordering': "['date', 'reps']", 'object_name': 'WorkoutLog'},
            'date': ('django.db.models.fields.DateField', [], {}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['exercises.Exercise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reps': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'weight': ('django.db.models.fields.DecimalField', [], {'max_digits': '5', 'decimal_places': '2'}),
            'workout': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['manager.TrainingSchedule']"})
        }
    }

    complete_apps = ['manager']