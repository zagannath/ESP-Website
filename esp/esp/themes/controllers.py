
__author__    = "Individual contributors (see AUTHORS file)"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "AGPL v.3"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2012 by the individual contributors
  (see AUTHORS file)

The ESP Web Site is free software; you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation; either version 3
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

Contact information:
MIT Educational Studies Program
  84 Massachusetts Ave W20-467, Cambridge, MA 02139
  Phone: 617-253-4882
  Email: esp-webmasters@mit.edu
Learning Unlimited, Inc.
  527 Franklin St, Cambridge, MA 02139
  Phone: 617-379-0178
  Email: web-team@lists.learningu.org
"""

from esp.utils.models import TemplateOverride
from esp.tagdict.models import Tag
from esp.themes import settings as themes_settings

from django.conf import settings
import cStringIO
import os
import re
import subprocess
import tempfile
import distutils.dir_util

THEME_DEBUG = True

class ThemeController(object):
    """
    This is a controller for manipulating the currently selected theme.
    """
    def __init__(self, *args, **kwargs):
        pass
        
    def get_current_theme(self):
        return Tag.getTag('current_theme_name', default='default')
        
    def get_theme_names(self):
        return os.listdir(settings.PROJECT_ROOT + 'esp/themes/theme_data/')
        
    def base_dir(self, theme_name):
        return settings.PROJECT_ROOT + 'esp/themes/theme_data/%s' % theme_name
        
    def list_filenames(self, dir, file_regexp, mask_base=False):
        result = []
        bd_len = len(dir)
        for dir_tup in os.walk(dir):
            for filename in dir_tup[2]:
                if re.search(file_regexp, filename):
                    if mask_base:
                        full_name = dir_tup[0][bd_len:] + filename
                    else:
                        full_name = dir_tup[0] + '/' + filename
                    result.append(full_name)
        return result
        
    def get_template_names(self, theme_name):
        return self.list_filenames(self.base_dir(theme_name) + '/templates', r'\.html$', mask_base=True)
        
    def global_less(self, search_dirs=None):
        if search_dirs is None:
            search_dirs = settings.LESS_SEARCH_PATH
        result = []
        for dir in search_dirs:
            result += self.list_filenames(dir, r'\.less$')
        return result
        
    def get_less_names(self, theme_name):
        result = []
        result += self.global_less()
        result.append(os.path.join(themes_settings.less_dir, 'variables.less'))
        result.append(os.path.join(themes_settings.less_dir, 'bootstrap.less'))
        result += self.list_filenames(self.base_dir(theme_name) + '/less', r'\.less$')
        return result
        
    def find_less_variables(self, theme_name):
        #   Return value is a mapping of names to default values (both strings)
        results = {}
        for filename in self.get_less_names(theme_name):
            local_results = {}
        
            #   Read less file
            less_file = open(filename)
            less_data = less_file.read()
            less_file.close()
            
            #   Find variable declarations
            for item in re.findall(r'@([a-zA-Z0-9_]+):(\s*)(.*?);', less_data):
                local_results[item[0]] = item[2]
                
            #   Store in a dictionary based on filename so we know where they came from
            results[filename] = local_results
                
        return results
        
    def compile_css(self, theme_name, variable_data, output_filename):
        #   Load LESS files in order of search path
        less_data = ''
        for filename in self.get_less_names(theme_name):
            less_file = open(filename)
            if THEME_DEBUG: print 'Including LESS source %s' % filename
            less_data += '\n' + less_file.read()
            less_file.close()
        
        if THEME_DEBUG:
            tf1 = open('debug_1.less', 'w')
            tf1.write(less_data)
            tf1.close()
            
        #   Replace all variable declarations for which we have a value defined
        for (variable_name, variable_value) in variable_data.iteritems():
            less_data = re.sub(r'@%s:(\s*)(.*?);' % variable_name, r'@%s: %s;' % (variable_name, variable_value), less_data)
            #   print 'Substituted value %s = %s' % (variable_name, variable_value)
        
        if THEME_DEBUG:
            tf1 = open('debug_2.less', 'w')
            tf1.write(less_data)
            tf1.close()
        
        (less_output_fd, less_output_filename) = tempfile.mkstemp()
        less_output_file = os.fdopen(less_output_fd, 'w')
        less_output_file.write(less_data)
        if THEME_DEBUG: print 'Wrote %d bytes to LESS file %s' % (len(less_data), less_output_filename)
        less_output_file.close()
        
        less_search_path = ', '.join([("'%s'" % dir.replace('\\', '/')) for dir in (settings.LESS_SEARCH_PATH + [os.path.join(settings.MEDIA_ROOT, 'theme_editor/less')])])
        
        js_code = """
var fs = require('fs');
var less = require('less');

var parser = new(less.Parser)({
    paths: [%s], // Specify search paths for @import directives
    filename: 'theme_compiled.less' // Specify a filename, for better error messages
});

var data = fs.readFileSync('%s', 'utf8');

parser.parse(data, function (e, tree) {
    console.log(tree.toCSS({ compress: true })); // Minify CSS output
});
        """ % (less_search_path, less_output_filename.replace('\\', '/'))
        
        #   print js_code
        
        #   Compile to CSS
        lessc_args = ["node"]
        lessc_process = subprocess.Popen(lessc_args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        css_data = lessc_process.communicate(input=js_code)[0]
        
        output_file = open(output_filename, 'w')
        output_file.write(css_data)
        output_file.close()
        if THEME_DEBUG: print 'Wrote %.1f KB CSS output to %s' % (len(css_data) / 1000., output_filename)

    def clear_theme(self, theme_name=None):
    
        if theme_name is None:
            theme_name = self.get_current_theme()
        
        #   Remove template overrides matching the theme name
        if THEME_DEBUG: print 'Clearing theme: %s' % theme_name
        for template_name in self.get_template_names(theme_name):
            TemplateOverride.objects.filter(name=template_name).delete()
            if THEME_DEBUG: print '-- Removed template override: %s' % template_name
        
        #   Remove images and script files from the active theme directory
        if os.path.exists(settings.MEDIA_ROOT + 'images/theme'):
            distutils.dir_util.remove_tree(settings.MEDIA_ROOT + 'images/theme')
        if os.path.exists(settings.MEDIA_ROOT + 'scripts/theme'):
            distutils.dir_util.remove_tree(settings.MEDIA_ROOT + 'scripts/theme')

        Tag.unSetTag('current_theme_name')

    def load_theme(self, theme_name, **kwargs):
    
        #   Create template overrides using data provided (our models handle versioning)
        if THEME_DEBUG: print 'Loading theme: %s' % theme_name
        for template_name in self.get_template_names(theme_name):
            to = TemplateOverride(name=template_name)
            to.content = open(self.base_dir(theme_name) + '/templates/' + template_name).read()
            #   print 'Template override %s contents: \n%s' % (to.name, to.content)
            to.save()
            if THEME_DEBUG: print '-- Created template override: %s' % template_name
            
        #   Collect LESS files from appropriate sources and compile CSS
        self.compile_css(theme_name, {}, settings.MEDIA_ROOT + 'styles/theme_compiled.css')
        
        #   Copy images and script files to the active theme directory
        if os.path.exists(self.base_dir(theme_name) + '/images'):
            distutils.dir_util.copy_tree(self.base_dir(theme_name) + '/images', settings.MEDIA_ROOT + 'images/theme')
        if os.path.exists(self.base_dir(theme_name) + '/scripts'):
            distutils.dir_util.copy_tree(self.base_dir(theme_name) + '/scripts', settings.MEDIA_ROOT + 'scripts/theme')

        Tag.setTag('current_theme_name', value=theme_name)

    def customize_theme(self, vars):
        self.compile_css(self.get_current_theme(), vars, settings.MEDIA_ROOT + 'styles/theme_compiled.css')
