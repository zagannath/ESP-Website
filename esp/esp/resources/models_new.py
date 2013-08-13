@reversion
class Resource(models.Model):
  """
  An instance of a physical resource, e.g. Chromebook #1, ADP2 Mac adapter, etc.
  All resources exist globally for use by all programs.
  """
  is_active = models.BooleanField()
  abstraction = models.ForeignKey(AbstractResource)
  identifier = models.CharField()
  # unique (abstraction, identifier) when is_active
  availability = models.ManyToManyField(Event)
  custom_attributes = models.JSONField()
  admin_custom_attributes = models.JSONField()
  description = models.TextField()
  notes = models.TextField()
  admin_notes = models.TextField()

@reversion
class AbstractResource(models.Model):
  """
  Represents an abstract version of a specific type of Resource, e.g. Thinkpad Linux computer, mini-display-port to VGA Mac adapter, 6' chalkboard, etc.
  Resources of the same AbstractResource are identical.
  All abstract resources exist globally for use by all programs.
  """
  is_active = models.BooleanField()
  resource_type = models.ForeignKey(ResourceType)
  name = models.CharField()
  # unique (resource_type, name) when is_active
  is_reusable = models.BooleanField()
  is_requestable = models.BooleanField()
  custom_attributes = models.JSONField()
  admin_custom_attributes = models.JSONField()
  description = models.TextField()
  notes = models.TextField()
  admin_notes = models.TextField()

@reversion
class ResourceType(models.Model):
  """
  Represents a type of resource, e.g. Linux computer, Mac adapter, chalkboard, etc.
  Distinct AbstractResources in the same ResourceType are similar and can potentially serve as substitutes, but are not identical.
  All resource types exist globally for use by all programs.
  """
  is_active = models.BooleanField()
  family = models.ForeignKey(ResourceFamily, null=True)
  name = models.CharField()
  # unique (resource_type, name) when is_active
  is_requestable = models.BooleanField()
  # if not family, then is_requestable
  custom_attributes = models.JSONField()
  admin_custom_attributes = models.JSONField()
  description = models.TextField()
  notes = models.TextField()
  admin_notes = models.TextField()

@reversion
class ResourceFamily(models.Model):
  """
  Represents a family of resources, e.g. computers, A/V, boards, etc.
  Resources descended from the same ResourceFamily have something in common, but are not necessarily substitutes.
  A ResourceType may, but is not required to, be a member of a ResourceFamily.
  A ResourceFamily may, but is not required to, be a member of a parent ResourceFamily.
  In this way, ResourceFamilies + ResourceTypes form a forest, with ResourceTypes as the leaves and with an arbitrary number of trees / roots.
  The trees will never be very tall, and probably not very wide, so this does not pose the problems that the DataTree has.
  All resource families exist globally for use by all programs.
  """
  is_active = models.BooleanField()
  parent = models.ForeignKey(ResourceFamily, null=True)
  name = models.CharField()
  # unique (resource_type, name) when is_active
  is_requestable = models.BooleanField()
  # if not family, then is_requestable
  custom_attributes = models.JSONField()
  admin_custom_attributes = models.JSONField()
  description = models.TextField()
  notes = models.TextField()
  admin_notes = models.TextField()

@reversion
class Location(models.Model):
  """
  A.k.a. a classroom.
  All locations exist globally for use by all programs.
  """
  is_active = models.BooleanField()
  area = models.ForeignKey(Area, null=True)
  name = models.CharField()
  # unique (area, name)
  display_name_override = models.CharField() # Some string template that includes %(location)s and, optionally, %(area)s; or the empty string. If not empty, overrides area.display_name.
  capacity = models.IntegerField()
  furnishings = property() # AbstractResources, ResourceTypes, and ResourceFamilies
  availability = models.ManyToManyField(Event)
  custom_attributes = models.JSONField()
  teacher_custom_attributes = models.JSONField()
  admin_custom_attributes = models.JSONField()
  description = models.TextField()
  notes = models.TextField()
  teacher_notes = models.TextField()
  admin_notes = models.TextField()
  is_requestable = models.BooleanField()
  url = models.URLField()
  administrator_email = models.EmailField()

@reversion
class Area(models.Model):
  """
  A.k.a. building, or floor, or wing, etc.
  A set of Locations that are sufficiently close together for scheduling purposes, and form some distinct geographic unit.
  All areas exist globally for use by all programs.
  """
  is_active = models.BooleanField()
  name = models.CharField()
  display_name = models.CharField() # Some string template that includes %(location)s and, optionally, %(area)s. Applied to all Locations in the area for their __unicode__ method.
  adjacent_areas = models.ManyToMany(symmetric=True) # Other sets of Locations that are also sufficiently close together for scheduling purposes, e.g. adjacent buildings.
  latitude = models.DecimalField()
  longitude = models.DecimalField()
  map_pixel_x = models.IntegerField()
  map_pixel_y = models.IntegerField()
  custom_attributes = models.JSONField()
  teacher_custom_attributes = models.JSONField()
  admin_custom_attributes = models.JSONField()
  description = models.TextField()
  notes = models.TextField()
  teacher_notes = models.TextField()
  admin_notes = models.TextField()
  is_requestable = models.BooleanField()
  url = models.URLField()
  administrator_email = models.EmailField()

@reversion
class Furnishing(models.Model):
  """
  A permanent, fixed resource in a Location.
  Global for all programs.
  Can be an AbstractResource, a ResourceType, or a ResourceFamily, depending on the level of detail that is cared about.
  """
  is_active = models.BooleanField()
  custom_attributes = models.JSONField()
  admin_custom_attributes = models.JSONField()
  description = models.TextField()
  notes = models.TextField()
  admin_notes = models.TextField()
  resource = models.ForeignKey(ContentType, choices=(AbstractResource,ResourceType,ResourceFamily))
  location = models.ForeignKey(Location)
  amount = models.IntegerField()

@reversion
class FloatingFurnishing(models.Model):
  """
  An assignment of a floating resource to a Location for some set of Events.
  """
  is_active = models.BooleanField()
  resource = models.ForeignKey(Resource)
  location = models.ForeignKey(Location)
  meeting_times = models.ManyToManyField(Event)
  ignore_warnings = models.BooleanField()
  lock_level = models.IntegerField() # for autoscheduler

@reversion
class ResourceAssignment(models.Model):
  """
  An assignment of a ClassSection to a Location and an Event, with Resources.
  """
  is_active = models.BooleanField()
  custom_attributes = models.JSONField()
  admin_custom_attributes = models.JSONField()
  notes = models.TextField()
  admin_notes = models.TextField()
  resource = models.ManyToManyFields(Resource)
  location = models.ForeignKey(Location)
  section = models.ForeignKey(ClassSection)
  meeting_time = models.ForeignKey(Event)
  # unique (resource, location, section) if is_active
  lock_level = models.IntegerField() # for autoscheduler
  ignore_warnings = models.BooleanField()

@reversion
class ResourceRequest(models.Model):
  """
  A request for a ClassSubject (all of its ClassSections) to be assigned a resource.
  Can be either an AbstractResource, ResourceType, or ResourceFamily, depending on the allowed and needed level of detail
  (the model object requested must have is_requestable == True).
  """
  is_active = models.BooleanField()
  resource = models.ForeignKey(ContentType, choices=(AbstractResource,ResourceType,ResourceFamily where is_requestable==True))
  subject = models.ForeignKey(ClassSubject)
  amount = models.IntegerField(null=True)
  pcnt_of_capacity = models.IntegerField(null=True)
  description = models.TextField()
  custom_attributes = models.JSONField()
  admin_custom_attributes = models.JSONField()
  notes = models.TextField()
  admin_notes = models.TextField()
  wont_satisfy = models.BooleanField(default=False) # set True if the request has been denied
  is_satisfied_override = models.TextField(blank=True, default="") # If the request has been satisfied, but the requested Resource can't be assigned on the website, then set this field as a non-empty explanation string
  
