__author__    = "Individual contributors (see AUTHORS file)"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "AGPL v.3"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2007 by the individual contributors
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

""" Models for Resources application """

from esp.cal.models import Event
from esp.users.models import User, ESPUser
from esp.db.fields import AjaxForeignKey
from esp.middleware import ESPError_Log
from esp.cache import cache_function
from esp.tagdict.models          import Tag

from django.db import models
from django.db.models.query import Q
from django.core.cache import cache

import pickle

########################################
#   New resource stuff (Michael P)
########################################

"""
Models (see more below):
    -   Resource types include classrooms, teacher availability, various equipment and furnishings.
    -   Resources are the individual "things"; the group id determines which are bunched together (such as a classroom and its big chalkboards).
    -   Resource requests ask for a particular filter on resources (including, by default, just their types).
    -   Resource assignments bind resources to events.
        
Procedures:
    -   Teacher availability module creates resources for each time slot a teacher is available for.
    -   Program resources module lets admin put in classrooms and equipment for the appropriate times.
"""

DISTANCE_FUNC_REGISTRY = {}

class ResourceType(models.Model):
    """ A type of resource (e.g.: Projector, Classroom, Box of Chalk) """
    from esp.survey.models import ListField

    name = models.CharField(max_length=40)                          #   Brief name
    description = models.TextField()                                #   What is this resource?
    consumable  = models.BooleanField(default = False)              #   Is this consumable?  (Not usable yet. -Michael P)
    priority_default = models.IntegerField(default=-1)  #   How important is this compared to other types?
    only_one = models.BooleanField(default=False, help_text="If set, in some cases, only allow adding one instance of this resource.")
    attributes_pickled  = models.TextField(default="Don't care", blank=True, help_text="A pipe (|) delimited list of possible attribute values.")       
    #   As of now we have a list of string choices for the value of a resource.  But in the future
    #   it could be extended.
    choices = ListField('attributes_pickled')
    program = models.ForeignKey('program.Program', null=True, blank=True)                 #   If null, this resource type is global.  Otherwise it's specific to one program.
    autocreated = models.BooleanField(default=False)
    distancefunc = models.TextField(
        blank=True,
        null=True,
        help_text="Enter python code that assumes <tt>r1</tt> and <tt>r2</tt> are resources with this type.",
        )               #   Defines a way to compare this resource type with others.

    def _get_attributes(self):
        if hasattr(self, '_attributes_cached'):
            return self._attributes_cached
        
        if self.attributes_pickled:
            try:
                self._attributes_cached = pickle.loads(self.attributes_pickled)
            except:
                self._attributes_cached = None
        else:
            self._attributes_cached = None

        return self._attributes_cached

    def _set_attributes(self, val):
        self._attributes_cached = val

    attributes = property(_get_attributes, _set_attributes)

    def save(self, *args, **kwargs):
        if hasattr(self, '_attributes_cached'):
            self.attributes_pickled = pickle.dumps(self._attributes_cached)
        super(ResourceType, self).save(*args, **kwargs)

    @staticmethod
    def get_or_create(label, program=None):
        if program:
            base_q = Q(program=program)
            if Tag.getTag('allow_global_restypes'):
                base_q = base_q | Q(program__isnull=True)
        else:
            base_q = Q(program__isnull=True)
        current_type = ResourceType.objects.filter(base_q).filter(name__icontains=label)
        if len(current_type) != 0:
            return current_type[0]
        else:
            nt = ResourceType()
            nt.name = label
            nt.description = ''
            nt.attributes_pickled = "Yes"
            nt.program = program
            nt.autocreated = True
            nt.save()
            return nt
        
    @staticmethod
    def global_types():
        return ResourceType.objects.filter(program__isnull=True)

    def __unicode__(self):
        return 'Resource Type "%s", priority=%d' % (self.name, self.priority_default)
    
    class Admin:
        pass

class ResourceRequest(models.Model):
    """ A request for a particular type of resource associated with a particular clas section. """
    
    target = models.ForeignKey('program.ClassSection', null=True)
    target_subj = models.ForeignKey('program.ClassSubject', null=True)
    res_type = models.ForeignKey(ResourceType)
    desired_value = models.TextField()
    
    def __unicode__(self):
        return 'Resource request of %s for %s: %s' % (unicode(self.res_type), self.target.emailcode(), self.desired_value)

    class Admin:
        pass
    
class Resource(models.Model):
    """ An individual resource, such as a class room or piece of equipment.  Categorize by
    res_type, attach to a user if necessary. """
    
    name = models.CharField(max_length=80)
    res_type = models.ForeignKey(ResourceType)
    num_students = models.IntegerField(blank=True, default=-1)
    group_id = models.IntegerField(default=-1) # Default value of -1 means ungrouped, or at least so I'm assuming for now in grouped_resources(). -ageng 2008-05-13
    is_unique = models.BooleanField(default=False)
    user = AjaxForeignKey(ESPUser, null=True, blank=True)
    event = models.ForeignKey(Event)
    
    def __unicode__(self):
        if self.user is not None:
            return 'For %s: %s (%s)' % (unicode(self.user), self.name, unicode(self.res_type))
        else:
            if self.num_students != -1:
                return 'For %d students: %s (%s)' % (self.num_students, self.name, unicode(self.res_type))
            else:
                return '%s (%s)' % (self.name, unicode(self.res_type))
    
    def save(self, *args, **kwargs):
        if self.group_id == -1:
            #   Give this a new group id.
            vals = Resource.objects.all().order_by('-group_id').values_list('group_id', flat=True)
            max_id = 0
            if len(vals) > 0:
                max_id = vals[0]
                
            self.group_id = max_id + 1
            self.is_unique = True
        else:
            self.is_unique = False

        super(Resource, self).save(*args, **kwargs)

    def distance(self, other):
        """
        Using the custom distance function defined in the ResourceType,
        compute the distance between this resource and another.
        Bear in mind that this is cached using a python global registry.
        """
        if self.res_type_id != other.res_type_id:
            raise ValueError("Both resources must be of the same type to compare!")

        if self.res_type_id in DISTANCE_FUNC_REGISTRY:
            return DISTANCE_FUNC_REGISTRY[self.res_type_id](self, other)

        distancefunc = self.res_type.distancefunc

        if distancefunc and distancefunc.strip():
            funcstr = distancefunc.strip().replace('\r\n', '\n')
        else:
            funcstr = "return 0"
        funcstr = """def _cmpfunc(r1, r2):\n%s""" % (
            '\n'.join('    %s' % l for l in funcstr.split('\n'))
            )
        exec funcstr
        DISTANCE_FUNC_REGISTRY[self.res_type_id] = _cmpfunc
        return _cmpfunc(self, other)

    __sub__ = distance


    def identical_resources(self):
        res_list = Resource.objects.filter(name=self.name)
        return res_list
    
    def satisfies_requests(self, req_class):
        #   Returns a list of 2 items.  The first element is boolean and the second element is a list of the unsatisfied requests.
        #   If there are no unsatisfied requests but the room isn't big enough, the first element will be false.

        result = [True, []]
        request_list = req_class.getResourceRequests()
        furnishings = self.associated_resources()
        id_list = []

        for req in request_list:
            if furnishings.filter(res_type=req.res_type).count() < 1:
                result[0] = False
                id_list.append(req.id)
        
        result[1] = ResourceRequest.objects.filter(id__in=id_list)

        if self.num_students < req_class.num_students():
            result[0] = False
        
        return result
    
    def grouped_resources(self):
        if self.group_id == -1:
            return Resource.objects.filter(id=self.id)
        return Resource.objects.filter(group_id=self.group_id)
    
    def associated_resources(self):
        return self.grouped_resources().exclude(id=self.id).exclude(res_type__name='Classroom')
    
    #   Modified to handle assigning rooms to both classes and their individual sections.
    #   Resource assignments are always handled at the section level now. 
    #   The assign_to_class function is copied for backwards compatibility.
    
    def assign_to_subject(self, new_class, check_constraint=True):
        for sec in new_class.sections.all():
            self.assign_to_section(sec, check_constraint)
        
    def assign_to_section(self, section, check_constraint=True, override=False):
        if override:
            self.clear_assignments()
        if self.is_available():
            new_ra = ResourceAssignment()
            new_ra.resource = self
            new_ra.target = section
            new_ra.save()
        else:
            raise ESPError_Log, 'Attempted to assign class section %d to conflicted resource; and constraint check was on.' % section.id
        
    assign_to_class = assign_to_section
        
    def clear_assignments(self, program=None):
        self.assignments().delete()

    def assignments(self):
        return ResourceAssignment.objects.filter(resource__in=self.grouped_resources())
    
    def schedule_sequence(self, program):
        """ Returns a list of strings, which are the status of the room (and its identical
        companions) at each time block belonging to the program. """

        sequence = []
        event_list = list(program.getTimeSlots())
        room_list = self.identical_resources().filter(event__in=event_list)
        for timeslot in event_list:
            single_room = room_list.filter(event=timeslot)
            if single_room.count() == 1:
                room = single_room[0]
                asl = list(room.assignments())
            
                if len(asl) == 0:
                    sequence.append('Empty')
                elif len(asl) == 1:
                    sequence.append(asl[0].getTargetOrSubject().emailcode())
                else:
                    init_str = 'Conflict: '
                    for ra in asl:
                        init_str += ra.getTargetOrSubject().emailcode() + ' '
                    sequence.append(init_str)
            else:
                sequence.append('N/A')
                
        return sequence
    
    def is_conflicted(self):
        return (self.assignments().count() > 1)
    
    def available_any_time(self, program=None):
        return (len(self.available_times(program)) > 0)
    
    def available_times_html(self, program=None):
        return '<br /> '.join([unicode(e) for e in Event.collapse(self.available_times(program))])

    def available_times(self, program=None):
        event_list = filter(lambda x: self.is_available(timeslot=x), list(self.matching_times(program)))
        return event_list
    
    def matching_times(self, program=None):
        #   Find all times for which a resource of the same name is available.
        event_list = self.identical_resources().values_list('event', flat=True)
        if program:
            return Event.objects.filter(id__in=event_list, program=program).order_by('start')
        else:
            return Event.objects.filter(id__in=event_list).order_by('start')
    
    def is_independent(self):
        if self.is_unique:
            return True
        else:
            return False
        
    @cache_function
    def is_available(self, QObjects=False, timeslot=None):
        if timeslot is None:
            test_resource = self
        else:
            test_resource = self.identical_resources().filter(event=timeslot)[0]
        
        if QObjects:
            return ~Q(test_resource.is_taken(True))
        else:
            return not test_resource.is_taken(False)
    is_available.depend_on_row(lambda:ResourceAssignment, lambda instance: {'self': instance.resource})
    is_available.depend_on_row(lambda:Event, lambda instance: {'timeslot': instance})
    
    def is_taken(self, QObjects=False):
        if QObjects:
            return Q(resource=self)
        else:
            collision = ResourceAssignment.objects.filter(resource=self)
            return (collision.count() > 0)
    
    class Admin:
        pass
    
class ResourceAssignment(models.Model):
    """ The binding of a resource to the class that it belongs to. """
    
    resource = models.ForeignKey(Resource)     #   Note: this really points to a bunch of Resources.
                                               #   See resources() below.
                                               
    target = models.ForeignKey('program.ClassSection', null=True)
    target_subj = models.ForeignKey('program.ClassSubject', null=True)
    lock_level = models.IntegerField(default=0)

    def __unicode__(self):
        result = u'Resource assignment for %s' % unicode(self.getTargetOrSubject())
        if self.lock_level > 0:
            result += u' (locked)'
        return result
    
    def getTargetOrSubject(self):
        """ Returns the most finely specified target. (target if it's set, target_subj otherwise) """
        if self.target is not None:
            return self.target
        return self.target_subj
    
    def resources(self):
        return Resource.objects.filter(group_id=self.resource.group_id)
    
    class Admin:
        pass
    
    
def install():
    #   Create default resource types.
    ResourceType.objects.get_or_create(name='Classroom',description='Type of classroom',attributes_pickled='Lecture|Discussion|Outdoor|Lab|Open space')
    ResourceType.objects.get_or_create(name='A/V',description='A/V equipment',attributes_pickled='LCD projector|Overhead projector|Amplified speaker|VCR|DVD player')
    ResourceType.objects.get_or_create(name='Computer[s]',description='Computer[s]',attributes_pickled='ESP laptop|Athena workstation|Macs for students|Windows PCs for students|Linux PCs for students')
    ResourceType.objects.get_or_create(name='Seating',description='Seating arrangement',attributes_pickled="Don't care|Fixed seats|Movable desks")
    ResourceType.objects.get_or_create(name='Light control',description='Light control',attributes_pickled="Don't care|Darkenable")
    
########################################
#   New new resource stuff (August 2013)
########################################

@reversion # Keep all previous versions of all objects, along with who made changes and when.
class HistoryPreservingModel(models.Model): # All resource models will inherit from here, i.e. all models below have these properties.
  is_active = models.BooleanField(default=True, help_text='Instead of deleting an object, set this to False. That way we retain access to old data and histories. Only objects with is_active=True will be used in views.')
  class Meta:
    abstract = True

class NewResource(HistoryPreservingModel):
  """
  An instance of a physical resource, e.g. Chromebook #1, ADP2 Mac adapter, etc.
  All resources exist globally for use by all programs.
  """
  abstraction = models.ForeignKey(AbstractResource)
  identifier = models.CharField()
  # unique (abstraction, identifier) when is_active
  availability = models.ManyToManyField(Event, help_text='All of the meeting times when this resource can be assigned to a class.') # Don't bother with a through model, because we can keep revisions here, and we don't need extra attributes for the through relation.
  description = models.TextField(blank=True, default='', help_text='A description of the resource to be viewable by admins and teachers.')

class AbstractResource(HistoryPreservingModel):
  """
  Represents an abstract version of a specific type of NewResource, e.g. Thinkpad Linux computer, mini-display-port to VGA Mac adapter, 6' chalkboard, etc.
  Resources of the same AbstractResource are identical.
  All abstract resources exist globally for use by all programs.
  """
  resource_type = models.ForeignKey(NewResourceType)
  name = models.CharField()
  # unique (resource_type, name) when is_active
  is_reusable = models.BooleanField(default=False, help_text="Can this resource be assigned more than once, or will its use in a class destroy it (such as a food item)? This defaults to True (can be reused), with the possibility of it being False (can't be reused, its use destroys it).")
  is_requestable = models.BooleanField()
  description = models.TextField(blank=True, default='', help_text='A description of the abstract resource to be viewable by admins and teachers.')
  furnishings = generic.GenericRelation(Furnishing, content_type_field='resource_content_type', object_id_field='resource_object_id', help_text='All of the furnishings of this AbstractResource.')
  requests = generic.GenericRelation(NewResourceRequest, content_type_field='resource_content_type', object_id_field='resource_object_id', help_text='All of the requests for this AbstractResource.')

class NewResourceType(HistoryPreservingModel):
  """
  Represents a type of resources, e.g. computers, A/V, boards, etc.
  Resources descended from the same NewResourceType have something in common, but are not necessarily substitutes.
  A NewResourceType may, but is not required to, be a member of a parent NewResourceType.
  In this way, ResourceTypes form a forest with an arbitrary number of trees / roots.
  The trees will never be very tall, and probably not very wide, so this does not pose the problems that the DataTree has.
  All resource types exist globally for use by all programs.
  """
  parent = models.ForeignKey(NewResourceType, null=True)
  name = models.CharField()
  # unique (resource_type, name) when is_active
  is_reusable = models.BooleanField(default=False, help_text="Can this resource be assigned more than once, or will its use in a class destroy it (such as a food item)? This defaults to True (can be reused), with the possibility of it being False (can't be reused, its use destroys it).")
  is_requestable = models.BooleanField()
  is_substitutable = models.BooleanField(default=False, help_text="Can descendants be safely substituted for one another in most cases? For example, projectors can be substitutable, but A/V can't be.")
  description = models.TextField(blank=True, default='', help_text='A description of the resource type to be viewable by admins and teachers.')
  furnishings = generic.GenericRelation(Furnishing, content_type_field='resource_content_type', object_id_field='resource_object_id', help_text='All of the furnishings of this NewResourceType.')
  requests = generic.GenericRelation(NewResourceRequest, content_type_field='resource_content_type', object_id_field='resource_object_id', help_text='All of the requests for this NewResourceType.')

class Location(HistoryPreservingModel):
  """
  A.k.a. a classroom.
  All locations exist globally for use by all programs.
  """
  area = models.ForeignKey(Area, null=True)
  name = models.CharField()
  # unique (area, name)
  display_template_override = models.CharField(blank=True, default='') # Some string template that includes %(location)s and, optionally, %(area)s; or the empty string. If not empty, overrides area.display_template.
  capacity = models.IntegerField()
  furnishings = property() # All AbstractResources, ResourceTypes that appear with this Location in the Furnishings table.
  availability = models.ManyToManyField(Event)
  description = models.TextField(blank=True, default='', help_text='A description of the location to be viewable by admins, teachers, volunteers, and students.')
  is_requestable = models.BooleanField()
  url = models.URLField()
  admins = models.ForeignKey(AreaAdministrator, null=True, help_text='The administrator or office that controls usage of this location.')

  def __unicode__(self):
    """
    display_template is self.display_template_override if it isn't blank;
    and is otherwise self.area.display_template.

    When printing the name of this Location, take display_template and
    replace all occurances of %(area)s with self.area.__unicode__(),
    and all occurances of %(location)s with self.name.
    """
    display_template = self.display_template_override or self.area.display_template
    return display_template % {'area': self.area, 'location': self.name}

class Area(HistoryPreservingModel):
  """
  A.k.a. building, or floor, or wing, etc.
  A set of Locations that are sufficiently close together for scheduling purposes, and form some distinct geographic unit.
  All areas exist globally for use by all programs.
  """
  name = models.CharField()
  display_template = models.CharField(default='%(area)s %(location)s') # Some string template that includes %(location)s and, optionally, %(area)s. Applied to all Locations in the area for their __unicode__ method. See Location.__unicode__()
  adjacent_areas = models.ManyToMany(symmetric=True) # Other sets of Locations that are also sufficiently close together for scheduling purposes, e.g. adjacent buildings.
  latitude = models.DecimalField(null=True, help_text='The latitude of the area, for lookup on an external map service.')
  longitude = models.DecimalField(null=True, help_text='The longitude of the area, for lookup on an external map service.')
  map_pixel_x = models.IntegerField(null=True, help_text='The x-coordinate pixel of this area on a campus map.')
  map_pixel_y = models.IntegerField(null=True, help_text='The y-coordinate pixel of this area on a campus map.')
  description = models.TextField(blank=True, default='', help_text='A description of the area to be viewable by anyone.')
  is_requestable = models.BooleanField()
  url = models.URLField(blank=True, help_text="The url to a campus-specific mapping website (e.g. whereis.mit.edu?go=2), or to the area's website.")
  admins = models.ForeignKey(AreaAdministrator, null=True, help_text='The administrator or office that controls usage of this area.')

  def __unicode__(self):
    return self.name

class Furnishing(HistoryPreservingModel):
  """
  A permanent, fixed resource in a Location.
  Global for all programs.
  Can be an AbstractResource or a NewResourceType, depending on the level of detail that is cared about.
  """
  description = models.TextField(blank=True, default='', help_text='A description of the furnishing to be viewable by admins and teachers.')

  # The following three combine into one field.
  resource_content_type = models.ForeignKey(ContentType, choices=(AbstractResource,NewResourceType))
  resource_object_id = models.PositiveIntegerField()
  resource = generic.GenericForeignKey('resource_content_type', 'resource_object_id', help_text='The furnished resource.')

  location = models.ForeignKey(Location)
  amount = models.IntegerField()

class NewResourceAssignment(HistoryPreservingModel):
  """
  An assignment of a ClassSection to a Location and an Event, with Resources.

  A NewResourceAssignment is needed for every (section, location, meeting_time)-tuple.
  This is equivalent to before (where sections were
  assigned to multiple (locations, meeting_time)-tuples), but is much clearer
  since the locations and meeting_times are now separate, stand-alone objects
  and are both represented explicitly in the assignment object. This does have
  the downside of requiring multiple NewResourceAssignment objects for multi-block
  classes, and needing to update multiple objects when moving a class to a new
  time or room. But this is not a regression from previous behavior. In fact,
  this should be easier to work with, since you just need to update the
  NewResourceAssignment objects by swapping the location and/or meeting_time,
  rather than needing to search for the correct (location, meeting_time)-pair and
  assigning that. For whatever hastle will still remain, I think the scheduling
  flexibility is worth it.

  Floating resources are assigned here too, rather than being separate. This
  gives the flexibility of being able to assign resources at a granular level.
  It will require care, to make sure that floating resources are assigned to
  all meeting_times where they are needed (which will usually be all of them).
  The to-be-provided methods for rescheduling a class will, by default, carry
  over the floating resources with them, but they can be dropped if the mover
  specifies that they should (perhaps because the new room has that resource
  built-in, or because that resource is not available in the new timeblock).
  Constraints checking will warn if resources are double-booked, assigned when
  not available, or different across time blocks (just in case it isn't
  intentional, in which case ignore_warnings can be set to True).
  """
  resource = models.ManyToManyFields(NewResource)
  location = models.ForeignKey(Location, help_text='The location of the class.')
  section = models.ForeignKey(ClassSection)
  meeting_time = models.ForeignKey(Event) # Replaces the meeting_times m2m field on ClassSection.
  # unique (resource, location, section) if is_active
  lock_level = models.IntegerField() # for autoscheduler
  ignore_warnings = models.BooleanField(default=False, help_text='If True, ignore warnings that would normally be generated from this assignment breaking constraints, such as scheduling two classes in the same classroom, if this broken constraint is deliberate.')
  meeting_point = models.ForeignKey(Location, null=True, help_text='The meeting point for teachers and students to gather at the beginning of class, before walking to the actual class location.')
  hide_location_from_students = models.BooleanField(default=False, help_true='Set this equal to True if the students should only be shown the meeting point, and not the location.')
  instructions = models.TextField(default='', help_text='For teachers (and students, if there is a meeting point and hide_location_from_students is False) to see, instructions for getting from the meeting point to the actual location, and any other important information.')

class NewResourceRequest(HistoryPreservingModel):
  """
  A request for a ClassSubject (all of its ClassSections) to be assigned a resource.
  Can be either an AbstractResource or NewResourceType, depending on the allowed and needed level of detail
  (the model object requested must have is_requestable == True).
  """
  # The following three combine into one field.
  resource_content_type = models.ForeignKey(ContentType, choices=(AbstractResource,NewResourceType))
  resource_object_id = models.PositiveIntegerField()
  resource = generic.GenericForeignKey('resource_content_type', 'resource_object_id', null=True, help_text='The requested resource.') # Target must have is_requestable==True. null if the resource doesn't exist in our system yet; should be described in "description"

  subject = models.ForeignKey(ClassSubject)
  amount = models.IntegerField(null=True)
  pcnt_of_capacity = models.IntegerField(null=True)
  required = models.BooleanField(default=True, help_text='Do you absolutely need this resource for your class?')
  description = models.TextField(blank=True, default='', help_text='A description of the resource request to be provided by teachers and viewable by admins.')
  wont_satisfy = models.BooleanField(default=False) # set True if the request has been denied
  is_satisfied_override = models.TextField(blank=True, default="") # If the request has been satisfied, but the requested NewResource can't be assigned on the website, then set this field as a non-empty explanation string

class AreaAdministrator(HistoryPreservingModel):
  name = models.CharField()
  emails = models.TextField(help_text='An email address or list of email addresses for this administrator')
  url = models.URLField()
  description = models.TextField(help_text='A description of an administrator for a set of areas/locations, viewable by admins.')
