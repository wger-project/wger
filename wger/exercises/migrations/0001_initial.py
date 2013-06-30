# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Language'
        db.create_table('exercises_language', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('short_name', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('full_name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal('exercises', ['Language'])

        # Adding model 'Muscle'
        db.create_table('exercises_muscle', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('is_front', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('exercises', ['Muscle'])

        # Adding model 'ExerciseCategory'
        db.create_table('exercises_exercisecategory', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exercises.Language'])),
        ))
        db.send_create_signal('exercises', ['ExerciseCategory'])

        # Adding model 'Exercise'
        db.create_table('exercises_exercise', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exercises.ExerciseCategory'])),
            ('description', self.gf('django.db.models.fields.TextField')(max_length=2000, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('exercises', ['Exercise'])

        # Adding M2M table for field muscles on 'Exercise'
        db.create_table('exercises_exercise_muscles', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('exercise', models.ForeignKey(orm['exercises.exercise'], null=False)),
            ('muscle', models.ForeignKey(orm['exercises.muscle'], null=False))
        ))
        db.create_unique('exercises_exercise_muscles', ['exercise_id', 'muscle_id'])

        # Adding M2M table for field muscles_secondary on 'Exercise'
        db.create_table('exercises_exercise_muscles_secondary', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('exercise', models.ForeignKey(orm['exercises.exercise'], null=False)),
            ('muscle', models.ForeignKey(orm['exercises.muscle'], null=False))
        ))
        db.create_unique('exercises_exercise_muscles_secondary', ['exercise_id', 'muscle_id'])

        # Adding model 'ExerciseComment'
        db.create_table('exercises_exercisecomment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('exercise', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exercises.Exercise'])),
            ('comment', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('exercises', ['ExerciseComment'])


    def backwards(self, orm):
        # Deleting model 'Language'
        db.delete_table('exercises_language')

        # Deleting model 'Muscle'
        db.delete_table('exercises_muscle')

        # Deleting model 'ExerciseCategory'
        db.delete_table('exercises_exercisecategory')

        # Deleting model 'Exercise'
        db.delete_table('exercises_exercise')

        # Removing M2M table for field muscles on 'Exercise'
        db.delete_table('exercises_exercise_muscles')

        # Removing M2M table for field muscles_secondary on 'Exercise'
        db.delete_table('exercises_exercise_muscles_secondary')

        # Deleting model 'ExerciseComment'
        db.delete_table('exercises_exercisecomment')


    models = {
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
        'exercises.exercisecomment': {
            'Meta': {'object_name': 'ExerciseComment'},
            'comment': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['exercises.Exercise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
        }
    }

    complete_apps = ['exercises']