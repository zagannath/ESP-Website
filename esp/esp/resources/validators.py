__author__    = "Individual contributors (see AUTHORS file)"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "AGPL v.3"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2013 by the individual contributors
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
  Email: web-team@learningu.org
"""

from django.core.validators import EMPTY_VALUES
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.utils.translation import ugettext_lazy as _

class ExactlyOneNotEmptyValidator(object):
  """
  A callable object that validates that, of a set of fields, exactly one of
  them has a value that is not empty.
  """
  message = _(u'Exactly one of %(verbose_names)s must not be empty.')
  code = 'invalid'
  def __init__(self, fields, message=None, code=None):
    """
    fields should be a dictionary with keys as field names,
    and values as verbose field names.
    """
    self.fields = fields
    if message is not None:
      self.message = message
    self.message = self.message % {'verbose_names': ', '.join(map(str, self.fields.values()))}
    if code is not None:
      self.code = code

  def __call__(self, *values):
    """
    Validates that, of the input values, exactly one of them must not be empty.
    """
    if len(filter(lambda value: value not in EMPTY_VALUES, values)) != 1:
      raise ValidationError(dict([(name, [self.message]) for name in self.fields.keys()+[NON_FIELD_ERRORS]]), code=self.code)
