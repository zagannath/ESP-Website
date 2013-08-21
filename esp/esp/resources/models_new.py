@reversion # Keep all previous versions of all objects, along with who made changes and when.
class HistoryPreservingModel(models.Model) # All resource models will inherit from here, i.e. all models below have these properties.
  is_active = models.BooleanField(default=True, help_text='Instead of deleting an object, set this to False. That way we retain access to old data and histories. Only objects with is_active=True will be used in views.')
  class Meta:
    abstract = True

class Resource(HistoryPreservingModel):
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
  Represents an abstract version of a specific type of Resource, e.g. Thinkpad Linux computer, mini-display-port to VGA Mac adapter, 6' chalkboard, etc.
  Resources of the same AbstractResource are identical.
  All abstract resources exist globally for use by all programs.
  """
  resource_type = models.ForeignKey(ResourceType)
  name = models.CharField()
  # unique (resource_type, name) when is_active
  is_reusable = models.BooleanField(default=False, help_text="Can this resource be assigned more than once, or will its use in a class destroy it (such as a food item)? This defaults to True (can be reused), with the possibility of it being False (can't be reused, its use destroys it).")
  is_requestable = models.BooleanField()
  description = models.TextField(blank=True, default='', help_text='A description of the abstract resource to be viewable by admins and teachers.')

class ResourceType(HistoryPreservingModel):
  """
  Represents a type of resource, e.g. Linux computer, Mac adapter, chalkboard, etc.
  Distinct AbstractResources in the same ResourceType are similar and can potentially serve as substitutes, but are not identical.
  All resource types exist globally for use by all programs.
  """
  family = models.ForeignKey(ResourceFamily, null=True)
  name = models.CharField()
  # unique (resource_type, name) when is_active
  is_requestable = models.BooleanField()
  # if not family, then is_requestable
  description = models.TextField(blank=True, default='', help_text='A description of the resource type to be viewable by admins and teachers.')

class ResourceFamily(HistoryPreservingModel):
  """
  Represents a family of resources, e.g. computers, A/V, boards, etc.
  Resources descended from the same ResourceFamily have something in common, but are not necessarily substitutes.
  A ResourceType may, but is not required to, be a member of a ResourceFamily.
  A ResourceFamily may, but is not required to, be a member of a parent ResourceFamily.
  In this way, ResourceFamilies + ResourceTypes form a forest, with ResourceTypes as the leaves and with an arbitrary number of trees / roots.
  The trees will never be very tall, and probably not very wide, so this does not pose the problems that the DataTree has.
  All resource families exist globally for use by all programs.
  """
  parent = models.ForeignKey(ResourceFamily, null=True)
  name = models.CharField()
  # unique (resource_type, name) when is_active
  is_requestable = models.BooleanField()
  # if not family, then is_requestable
  description = models.TextField(blank=True, default='', help_text='A description of the resource family to be viewable by admins and teachers.')

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
  furnishings = property() # AbstractResources, ResourceTypes, and ResourceFamilies
  availability = models.ManyToManyField(Event)
  description = models.TextField(blank=True, default='', help_text='A description of the location to be viewable by admins, teachers, volunteers, and students.')
  is_requestable = models.BooleanField()
  url = models.URLField()
  admins = models.ForeignKey(AreaAdministrativeGroup, null=True, help_text='The group that administrates this location and controls its usage, if different than that of the entire area.')

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
  admins = models.ForeignKey(AreaAdministrativeGroup, null=True, help_text='The group that administrates this area and controls its usage.')

  def __unicode__(self):
    return self.name

class Furnishing(HistoryPreservingModel):
  """
  A permanent, fixed resource in a Location.
  Global for all programs.
  Can be an AbstractResource, a ResourceType, or a ResourceFamily, depending on the level of detail that is cared about.
  """
  description = models.TextField(blank=True, default='', help_text='A description of the furnishing to be viewable by admins and teachers.')
  resource = models.ForeignKey(ContentType, choices=(AbstractResource,ResourceType,ResourceFamily))
  location = models.ForeignKey(Location)
  amount = models.IntegerField()

class ResourceAssignment(HistoryPreservingModel):
  """
  An assignment of a ClassSection to a Location and an Event, with Resources.

  A ResourceAssignment is needed for every (section, location, meeting_time)-tuple.
  This is equivalent to before (where sections were
  assigned to multiple (locations, meeting_time)-tuples), but is much clearer
  since the locations and meeting_times are now separate, stand-alone objects
  and are both represented explicitly in the assignment object. This does have
  the downside of requiring multiple ResourceAssignment objects for multi-block
  classes, and needing to update multiple objects when moving a class to a new
  time or room. But this is not a regression from previous behavior. In fact,
  this should be easier to work with, since you just need to update the
  ResourceAssignment objects by swapping the location and/or meeting_time,
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
  resource = models.ManyToManyFields(Resource)
  location = models.ForeignKey(Location, help_text='The location of the class.')
  section = models.ForeignKey(ClassSection)
  meeting_time = models.ForeignKey(Event) # Replaces the meeting_times m2m field on ClassSection.
  # unique (resource, location, section) if is_active
  lock_level = models.IntegerField() # for autoscheduler
  ignore_warnings = models.BooleanField(default=False, help_text='If True, ignore warnings that would normally be generated from this assignment breaking constraints, such as scheduling two classes in the same classroom, if this broken constraint is deliberate.')
  meeting_point = models.ForeignKey(Location, null=True, help_text='The meeting point for teachers and students to gather at the beginning of class, before walking to the actual class location.')
  hide_location_from_students = models.BooleanField(default=False, help_true='Set this equal to True if the students should only be shown the meeting point, and not the location.')
  instructions = models.TextField(default='', help_text='For teachers (and students, if there is a meeting point and hide_location_from_students is False) to see, instructions for getting from the meeting point to the actual location, and any other important information.')

class ResourceRequest(HistoryPreservingModel):
  """
  A request for a ClassSubject (all of its ClassSections) to be assigned a resource.
  Can be either an AbstractResource, ResourceType, or ResourceFamily, depending on the allowed and needed level of detail
  (the model object requested must have is_requestable == True).
  """
  resource = models.ForeignKey(ContentType, choices=(AbstractResource,ResourceType,ResourceFamily where is_requestable==True))
  subject = models.ForeignKey(ClassSubject)
  amount = models.IntegerField(null=True)
  pcnt_of_capacity = models.IntegerField(null=True)
  required = models.BooleanField(default=True, help_text='Do you absolutely need this resource for your class?')
  description = models.TextField(blank=True, default='', help_text='A description of the resource request to be provided by teachers and viewable by admins.')
  wont_satisfy = models.BooleanField(default=False) # set True if the request has been denied
  is_satisfied_override = models.TextField(blank=True, default="") # If the request has been satisfied, but the requested Resource can't be assigned on the website, then set this field as a non-empty explanation string

class AreaAdministrativeGroup(HistoryPreservingModel):
  name = models.CharField()
  email = models.EmailField()
  url = models.URLField()
  description = models.TextField(help_text='A description of the group of administrators for a set of areas/locations, viewable by admins.')

class AreaAdministrator(HistoryPreservingModel):
  name = models.CharField()
  email = models.EmailField()
  url = models.URLField()
  description = models.TextField(help_text='A description of an administrator for a set of areas/locations, viewable by admins.')
  group = models.ForeignKey()
