# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AbstractResource'
        db.create_table('resources_abstractresource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('resource_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['resources.NewResourceType'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('is_reusable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_requestable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('resources', ['AbstractResource'])

        # Adding model 'NewResource'
        db.create_table('resources_newresource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('abstraction', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['resources.AbstractResource'])),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('resources', ['NewResource'])

        # Adding M2M table for field availability on 'NewResource'
        db.create_table('resources_newresource_availability', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('newresource', models.ForeignKey(orm['resources.newresource'], null=False)),
            ('event', models.ForeignKey(orm['cal.event'], null=False))
        ))
        db.create_unique('resources_newresource_availability', ['newresource_id', 'event_id'])

        # Adding model 'AreaAdministrator'
        db.create_table('resources_areaadministrator', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('emails', self.gf('django.db.models.fields.TextField')()),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('resources', ['AreaAdministrator'])

        # Adding model 'NewResourceRequest'
        db.create_table('resources_newresourcerequest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('resource_content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('resource_object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('subject', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['program.ClassSubject'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('pcnt_of_capacity', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('required', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('wont_satisfy', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_satisfied_override', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('resources', ['NewResourceRequest'])

        # Adding model 'Furnishing'
        db.create_table('resources_furnishing', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('resource_content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('resource_object_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['resources.Location'])),
            ('amount', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('resources', ['Furnishing'])

        # Adding model 'Area'
        db.create_table('resources_area', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('display_template', self.gf('django.db.models.fields.CharField')(default='%(area)s %(location)s', max_length=128)),
            ('latitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=5)),
            ('longitude', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=8, decimal_places=5)),
            ('map_pixel_x', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('map_pixel_y', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('is_requestable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200, blank=True)),
            ('admins', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['resources.AreaAdministrator'], null=True)),
        ))
        db.send_create_signal('resources', ['Area'])

        # Adding M2M table for field adjacent_areas on 'Area'
        db.create_table('resources_area_adjacent_areas', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_area', models.ForeignKey(orm['resources.area'], null=False)),
            ('to_area', models.ForeignKey(orm['resources.area'], null=False))
        ))
        db.create_unique('resources_area_adjacent_areas', ['from_area_id', 'to_area_id'])

        # Adding model 'NewResourceAssignment'
        db.create_table('resources_newresourceassignment', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('location', self.gf('django.db.models.fields.related.ForeignKey')(related_name='location_newresourceassignment', to=orm['resources.Location'])),
            ('section', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['program.ClassSection'])),
            ('meeting_time', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['cal.Event'])),
            ('lock_level', self.gf('django.db.models.fields.IntegerField')()),
            ('ignore_warnings', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('meeting_point', self.gf('django.db.models.fields.related.ForeignKey')(related_name='meeting_point_newresourceassignment', null=True, to=orm['resources.Location'])),
            ('hide_location_from_students', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('instructions', self.gf('django.db.models.fields.TextField')(default='')),
        ))
        db.send_create_signal('resources', ['NewResourceAssignment'])

        # Adding M2M table for field resource on 'NewResourceAssignment'
        db.create_table('resources_newresourceassignment_resource', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('newresourceassignment', models.ForeignKey(orm['resources.newresourceassignment'], null=False)),
            ('newresource', models.ForeignKey(orm['resources.newresource'], null=False))
        ))
        db.create_unique('resources_newresourceassignment_resource', ['newresourceassignment_id', 'newresource_id'])

        # Adding model 'Location'
        db.create_table('resources_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('area', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['resources.Area'], null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('display_template_override', self.gf('django.db.models.fields.CharField')(default='', max_length=128, blank=True)),
            ('capacity', self.gf('django.db.models.fields.IntegerField')()),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
            ('is_requestable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('admins', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['resources.AreaAdministrator'], null=True)),
        ))
        db.send_create_signal('resources', ['Location'])

        # Adding M2M table for field availability on 'Location'
        db.create_table('resources_location_availability', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('location', models.ForeignKey(orm['resources.location'], null=False)),
            ('event', models.ForeignKey(orm['cal.event'], null=False))
        ))
        db.create_unique('resources_location_availability', ['location_id', 'event_id'])

        # Adding model 'NewResourceType'
        db.create_table('resources_newresourcetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['resources.NewResourceType'], null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('is_reusable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_requestable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_substitutable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('description', self.gf('django.db.models.fields.TextField')(default='', blank=True)),
        ))
        db.send_create_signal('resources', ['NewResourceType'])


    def backwards(self, orm):
        # Deleting model 'AbstractResource'
        db.delete_table('resources_abstractresource')

        # Deleting model 'NewResource'
        db.delete_table('resources_newresource')

        # Removing M2M table for field availability on 'NewResource'
        db.delete_table('resources_newresource_availability')

        # Deleting model 'AreaAdministrator'
        db.delete_table('resources_areaadministrator')

        # Deleting model 'NewResourceRequest'
        db.delete_table('resources_newresourcerequest')

        # Deleting model 'Furnishing'
        db.delete_table('resources_furnishing')

        # Deleting model 'Area'
        db.delete_table('resources_area')

        # Removing M2M table for field adjacent_areas on 'Area'
        db.delete_table('resources_area_adjacent_areas')

        # Deleting model 'NewResourceAssignment'
        db.delete_table('resources_newresourceassignment')

        # Removing M2M table for field resource on 'NewResourceAssignment'
        db.delete_table('resources_newresourceassignment_resource')

        # Deleting model 'Location'
        db.delete_table('resources_location')

        # Removing M2M table for field availability on 'Location'
        db.delete_table('resources_location_availability')

        # Deleting model 'NewResourceType'
        db.delete_table('resources_newresourcetype')


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
        'cal.event': {
            'Meta': {'object_name': 'Event'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'event_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cal.EventType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['program.Program']", 'null': 'True', 'blank': 'True'}),
            'short_description': ('django.db.models.fields.TextField', [], {}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'cal.eventtype': {
            'Meta': {'object_name': 'EventType'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'datatree.datatree': {
            'Meta': {'unique_together': "(('name', 'parent'),)", 'object_name': 'DataTree'},
            'friendly_name': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lock_table': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'child_set'", 'null': 'True', 'to': "orm['datatree.DataTree']"}),
            'range_correct': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'rangeend': ('django.db.models.fields.IntegerField', [], {}),
            'rangestart': ('django.db.models.fields.IntegerField', [], {}),
            'uri': ('django.db.models.fields.CharField', [], {'max_length': '1024'}),
            'uri_correct': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'program.classcategories': {
            'Meta': {'object_name': 'ClassCategories'},
            'category': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'seq': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'symbol': ('django.db.models.fields.CharField', [], {'default': "'?'", 'max_length': '1'})
        },
        'program.classsection': {
            'Meta': {'ordering': "['id']", 'object_name': 'ClassSection'},
            'anchor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['datatree.DataTree']", 'null': 'True', 'blank': 'True'}),
            'checklist_progress': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['program.ProgramCheckItem']", 'symmetrical': 'False', 'blank': 'True'}),
            'duration': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'enrolled_students': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_class_capacity': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'meeting_times': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'meeting_times'", 'blank': 'True', 'to': "orm['cal.Event']"}),
            'parent_class': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sections'", 'to': "orm['program.ClassSubject']"}),
            'registration_status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'registrations': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'through': "orm['program.StudentRegistration']", 'symmetrical': 'False'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'program.classsizerange': {
            'Meta': {'object_name': 'ClassSizeRange'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['program.Program']", 'null': 'True', 'blank': 'True'}),
            'range_max': ('django.db.models.fields.IntegerField', [], {}),
            'range_min': ('django.db.models.fields.IntegerField', [], {})
        },
        'program.classsubject': {
            'Meta': {'object_name': 'ClassSubject', 'db_table': "'program_class'"},
            'allow_lateness': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'allowable_class_size_ranges': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'classsubject_allowedsizes'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['program.ClassSizeRange']"}),
            'anchor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['datatree.DataTree']", 'null': 'True', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cls'", 'to': "orm['program.ClassCategories']"}),
            'checklist_progress': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['program.ProgramCheckItem']", 'symmetrical': 'False', 'blank': 'True'}),
            'class_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'class_size_max': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'class_size_min': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'class_size_optimal': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'custom_form_data': ('esp.utils.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'directors_notes': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'duration': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '5', 'decimal_places': '2', 'blank': 'True'}),
            'grade_max': ('django.db.models.fields.IntegerField', [], {}),
            'grade_min': ('django.db.models.fields.IntegerField', [], {}),
            'hardness_rating': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting_times': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cal.Event']", 'symmetrical': 'False', 'blank': 'True'}),
            'message_for_directors': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'optimal_class_size_range': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['program.ClassSizeRange']", 'null': 'True', 'blank': 'True'}),
            'parent_program': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['program.Program']"}),
            'prereqs': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'purchase_requests': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'requested_room': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'requested_special_resources': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'schedule': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'session_count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'teachers': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'program.program': {
            'Meta': {'object_name': 'Program'},
            'anchor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['datatree.DataTree']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'class_categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['program.ClassCategories']", 'symmetrical': 'False'}),
            'director_email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'grade_max': ('django.db.models.fields.IntegerField', [], {}),
            'grade_min': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'program_allow_waitlist': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'program_modules': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['program.ProgramModule']", 'symmetrical': 'False'}),
            'program_size_max': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'program.programcheckitem': {
            'Meta': {'ordering': "('seq',)", 'object_name': 'ProgramCheckItem'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'checkitems'", 'to': "orm['program.Program']"}),
            'seq': ('django.db.models.fields.PositiveIntegerField', [], {'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '512'})
        },
        'program.programmodule': {
            'Meta': {'object_name': 'ProgramModule'},
            'admin_title': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'handler': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inline_template': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'link_title': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'module_type': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'seq': ('django.db.models.fields.IntegerField', [], {})
        },
        'program.registrationtype': {
            'Meta': {'unique_together': "(('name', 'category'),)", 'object_name': 'RegistrationType'},
            'category': ('django.db.models.fields.CharField', [], {'max_length': '32'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'displayName': ('django.db.models.fields.CharField', [], {'max_length': '32', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '32'})
        },
        'program.studentregistration': {
            'Meta': {'object_name': 'StudentRegistration'},
            'end_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(9999, 1, 1, 0, 0)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'relationship': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['program.RegistrationType']"}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['program.ClassSection']"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'qsdmedia.media': {
            'Meta': {'object_name': 'Media'},
            'anchor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['datatree.DataTree']", 'null': 'True', 'blank': 'True'}),
            'file_extension': ('django.db.models.fields.TextField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'file_name': ('django.db.models.fields.TextField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'format': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'friendly_name': ('django.db.models.fields.TextField', [], {}),
            'hashed_name': ('django.db.models.fields.TextField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mime_type': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True', 'blank': 'True'}),
            'owner_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'size': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'target_file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'})
        },
        'resources.abstractresource': {
            'Meta': {'object_name': 'AbstractResource'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_requestable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_reusable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'resource_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.NewResourceType']"})
        },
        'resources.area': {
            'Meta': {'object_name': 'Area'},
            'adjacent_areas': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'adjacent_areas_rel_+'", 'to': "orm['resources.Area']"}),
            'admins': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.AreaAdministrator']", 'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'display_template': ('django.db.models.fields.CharField', [], {'default': "'%(area)s %(location)s'", 'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_requestable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'latitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '5'}),
            'longitude': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '8', 'decimal_places': '5'}),
            'map_pixel_x': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'map_pixel_y': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'})
        },
        'resources.areaadministrator': {
            'Meta': {'object_name': 'AreaAdministrator'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'emails': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'resources.furnishing': {
            'Meta': {'object_name': 'Furnishing'},
            'amount': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.Location']"}),
            'resource_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'resource_object_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'resources.location': {
            'Meta': {'object_name': 'Location'},
            'admins': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.AreaAdministrator']", 'null': 'True'}),
            'area': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.Area']", 'null': 'True'}),
            'availability': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cal.Event']", 'symmetrical': 'False'}),
            'capacity': ('django.db.models.fields.IntegerField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'display_template_override': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '128', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_requestable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'resources.newresource': {
            'Meta': {'object_name': 'NewResource'},
            'abstraction': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.AbstractResource']"}),
            'availability': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['cal.Event']", 'symmetrical': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        'resources.newresourceassignment': {
            'Meta': {'object_name': 'NewResourceAssignment'},
            'hide_location_from_students': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ignore_warnings': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'instructions': ('django.db.models.fields.TextField', [], {'default': "''"}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'location': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'location_newresourceassignment'", 'to': "orm['resources.Location']"}),
            'lock_level': ('django.db.models.fields.IntegerField', [], {}),
            'meeting_point': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meeting_point_newresourceassignment'", 'null': 'True', 'to': "orm['resources.Location']"}),
            'meeting_time': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cal.Event']"}),
            'resource': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['resources.NewResource']", 'symmetrical': 'False'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['program.ClassSection']"})
        },
        'resources.newresourcerequest': {
            'Meta': {'object_name': 'NewResourceRequest'},
            'amount': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_satisfied_override': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'pcnt_of_capacity': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'required': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'resource_content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'resource_object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'subject': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['program.ClassSubject']"}),
            'wont_satisfy': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        'resources.newresourcetype': {
            'Meta': {'object_name': 'NewResourceType'},
            'description': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_requestable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_reusable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_substitutable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.NewResourceType']", 'null': 'True'})
        },
        'resources.resource': {
            'Meta': {'object_name': 'Resource'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['cal.Event']"}),
            'group_id': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_unique': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'num_students': ('django.db.models.fields.IntegerField', [], {'default': '-1', 'blank': 'True'}),
            'res_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.ResourceType']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        'resources.resourceassignment': {
            'Meta': {'object_name': 'ResourceAssignment'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lock_level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'resource': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.Resource']"}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['program.ClassSection']", 'null': 'True'}),
            'target_subj': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['program.ClassSubject']", 'null': 'True'})
        },
        'resources.resourcerequest': {
            'Meta': {'object_name': 'ResourceRequest'},
            'desired_value': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'res_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['resources.ResourceType']"}),
            'target': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['program.ClassSection']", 'null': 'True'}),
            'target_subj': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['program.ClassSubject']", 'null': 'True'})
        },
        'resources.resourcetype': {
            'Meta': {'object_name': 'ResourceType'},
            'attributes_pickled': ('django.db.models.fields.TextField', [], {'default': '"Don\'t care"', 'blank': 'True'}),
            'autocreated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'consumable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'distancefunc': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '40'}),
            'only_one': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'priority_default': ('django.db.models.fields.IntegerField', [], {'default': '-1'}),
            'program': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['program.Program']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['resources']