
__author__    = "MIT ESP"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "GPL v.2"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2007 MIT ESP

The ESP Web Site is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

Contact Us:
ESP Web Group
MIT Educational Studies Program,
84 Massachusetts Ave W20-467, Cambridge, MA 02139
Phone: 617-253-4882
Email: web@esp.mit.edu
"""
from esp.program.modules.base    import ProgramModuleObj, needs_admin, main_call, aux_call, meets_deadline, needs_student
from esp.program.modules         import module_ext
from esp.program.models          import Program, ClassSubject, ClassSection, ClassCategories
from esp.program.views           import lottery_student_reg, lsr_submit
from esp.datatree.models         import *
from esp.web.util                import render_to_response
from django                      import forms
from django.http                 import HttpResponseRedirect, HttpResponse
from django.template.loader      import render_to_string
from esp.cal.models              import Event
from esp.users.models            import User, ESPUser, UserBit, UserAvailability
from esp.middleware              import ESPError
from esp.resources.models        import Resource, ResourceRequest, ResourceType, ResourceAssignment
from esp.datatree.models         import DataTree
from datetime                    import timedelta
from django.utils                import simplejson
from collections                 import defaultdict
from esp.cache                   import cache_function
from uuid                        import uuid4 as get_uuid

class LotteryStudentRegModule(ProgramModuleObj):

    @classmethod
    def module_properties(cls):
        return {
            "link_title": "Class Registration Lottery",
            "admin_title": "Lottery Student Registration",
            "module_type": "learn",
            "seq": 7
            }
    
        """ def prepare(self, context={}):
        if context is None: context = {}

        context['schedulingmodule'] = self 
        return context """

    @main_call
    @needs_student
    @meets_deadline('/Classes/Lottery')
    def lotterystudentreg(self, request, tl, one, two, module, extra, prog):
        """
        Serve the student reg page.

        This is just a static page;
        it gets all of its content from AJAX callbacks.
        """

        print "blooble"
        print request.user.username
        return lottery_student_reg(request, self.program)

    @aux_call
    @meets_deadline('/Classes/Lottery')
    def lsrsubmit(self, request, tl, one, two, module, extra, prog):
        """
        Currently a placeholder; someday this will get looped in
        to the actual lottery student reg so that it gets called.
        """

        return lsr_submit(request, self.program)


