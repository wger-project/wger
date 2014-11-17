# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AdminUserNote'
        db.create_table(u'gym_adminusernote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='adminusernote_user', to=orm['auth.User'])),
            ('member', self.gf('django.db.models.fields.related.ForeignKey')(related_name='adminusernote_member', to=orm['auth.User'])),
            ('timestamp_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('timestamp_edited', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'gym', ['AdminUserNote'])


    def backwards(self, orm):
        # Deleting model 'AdminUserNote'
        db.delete_table(u'gym_adminusernote')


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
        u'gym.adminusernote': {
            'Meta': {'ordering': "['-timestamp_created']", 'object_name': 'AdminUserNote'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'adminusernote_member'", 'to': u"orm['auth.User']"}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'timestamp_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'timestamp_edited': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'adminusernote_user'", 'to': u"orm['auth.User']"})
        },
        u'gym.gym': {
            'Meta': {'ordering': "['name']", 'object_name': 'Gym'},
            'city': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'owner': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'zip_code': ('django.db.models.fields.IntegerField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'})
        },
        u'gym.gymadminconfig': {
            'Meta': {'unique_together': "(('gym', 'user'),)", 'object_name': 'GymAdminConfig'},
            'gym': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gym.Gym']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'overview_inactive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        },
        u'gym.gymconfig': {
            'Meta': {'object_name': 'GymConfig'},
            'gym': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'config'", 'unique': 'True', 'to': u"orm['gym.Gym']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'weeks_inactive': ('django.db.models.fields.PositiveIntegerField', [], {'default': '4', 'max_length': '2'})
        },
        u'gym.gymuserconfig': {
            'Meta': {'unique_together': "(('gym', 'user'),)", 'object_name': 'GymUserConfig'},
            'gym': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['gym.Gym']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_inactive': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['gym']