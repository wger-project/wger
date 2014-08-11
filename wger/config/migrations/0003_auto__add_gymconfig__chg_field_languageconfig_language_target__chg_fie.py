# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'GymConfig'
        db.create_table(u'config_gymconfig', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('default_gym', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Gym'], null=True, blank=True)),
        ))
        db.send_create_signal(u'config', ['GymConfig'])


        # Changing field 'LanguageConfig.language_target'
        db.alter_column(u'config_languageconfig', 'language_target_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Language']))

        # Changing field 'LanguageConfig.language'
        db.alter_column(u'config_languageconfig', 'language_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Language']))

    def backwards(self, orm):
        # Deleting model 'GymConfig'
        db.delete_table(u'config_gymconfig')


        # Changing field 'LanguageConfig.language_target'
        db.alter_column(u'config_languageconfig', 'language_target_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exercises.Language']))

        # Changing field 'LanguageConfig.language'
        db.alter_column(u'config_languageconfig', 'language_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['exercises.Language']))

    models = {
        u'config.gymconfig': {
            'Meta': {'object_name': 'GymConfig'},
            'default_gym': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Gym']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'config.languageconfig': {
            'Meta': {'ordering': "['item', 'language_target']", 'object_name': 'LanguageConfig'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'language_source'", 'to': u"orm['core.Language']"}),
            'language_target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'language_target'", 'to': u"orm['core.Language']"}),
            'show': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'core.gym': {
            'Meta': {'object_name': 'Gym'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'owner': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.IntegerField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        u'core.language': {
            'Meta': {'ordering': "['full_name']", 'object_name': 'Language'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        }
    }

    complete_apps = ['config']