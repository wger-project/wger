# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LanguageConfig'
        db.create_table(u'config_languageconfig', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('language', self.gf('django.db.models.fields.related.ForeignKey')(related_name='laguage_source', to=orm['exercises.Language'])),
            ('language_target', self.gf('django.db.models.fields.related.ForeignKey')(related_name='laguage_target', to=orm['exercises.Language'])),
            ('item', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('show', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'config', ['LanguageConfig'])


    def backwards(self, orm):
        # Deleting model 'LanguageConfig'
        db.delete_table(u'config_languageconfig')


    models = {
        u'config.languageconfig': {
            'Meta': {'object_name': 'LanguageConfig'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'language': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'laguage_source'", 'to': u"orm['exercises.Language']"}),
            'language_target': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'laguage_target'", 'to': u"orm['exercises.Language']"}),
            'show': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'exercises.language': {
            'Meta': {'object_name': 'Language'},
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'short_name': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        }
    }

    complete_apps = ['config']
