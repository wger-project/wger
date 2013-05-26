# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        '''
        By default, all languages only show exercises and ingredients in
        that same language.
        '''
        for language_source in orm['exercises.Language'].objects.all():
            for language_target in orm['exercises.Language'].objects.all():
                for item in ('1', '2'):
                    config = orm.Languageconfig()
                    config.language = language_source
                    config.language_target = language_target
                    config.item = item[0]
                    if language_source == language_target:
                        config.show = True
                    else:
                        config.show = False
                    config.save()
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."

    def backwards(self, orm):
        "Write your backwards methods here."
        db.clear_table('config_languageconfig')

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
    symmetrical = True
