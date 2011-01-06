
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

from esp.section_data import section_redirect_keys, subsection_map

def extract_subsection(url):
	"""
	Given a url, return (url without subsection, subsection).

	The subsection, if present, is the first path element and is one of
	the keys found in esp.section_data.subsection_map.

	"""
	# Preprocess the URL: strip spaces and leading slash
	url = url.strip()
	if url[0] == '/':
		url = url[1:]
	# Extract subsection
	parts = url.split('/', 1)
	if parts[0] in section_redirect_keys:
		subsection = parts.pop(0)
	else:
		subsection = None
	return ('/'.join(parts), subsection)

def get_branch_info(url, subsection=None):
    """
    Given URL info, map to the DataTree and extract related info.

    Given:
        * Optional subsection (learn, teach, program(s), help, manage, onsite)
        * A URL that doesn't contain the subsection
    Find:
        * A datatree URI
        * A "view address" (read: "filename")
        * The subsection, possibly translated
        * An action (create, edit, read (see branch_find below)).

    """
    DEFAULT_ACTION = 'read'

    # Extract a datatree URI
    section = section_redirect_keys[subsection]
    tree_root = 'Q/' + section
    tree_end = url.split('/')
    view_address = tree_end.pop()
    if not view_address.strip():
        return None  # empty final component is invalid
    tree_node_uri = tree_root + '/' + '/'.join(tree_end)

    # Extract an action
    view_address_pieces = view_address.split('.')
    if len(view_address_pieces) > 1:
        action       = view_address_pieces[-1]
        view_address = '.'.join(view_address_pieces[:-1])
    else:
        action       = DEFAULT_ACTION
        view_address = view_address_pieces[0]

    # Rewrite 'subsection' if we want to.
    if subsection_map.has_key(subsection):
        subsection = subsection_map[subsection]

    # Tag the view address with the (rewritten) subsection
    if subsection:
        view_address = "%s:%s" % (subsection, view_address)

    return (tree_node_uri, view_address, subsection, action)
