__author__    = "Individual contributors (see AUTHORS file)"
__date__      = "$DATE$"
__rev__       = "$REV$"
__license__   = "AGPL v.3"
__copyright__ = """
This file is part of the ESP Web Site
Copyright (c) 2009 by the individual contributors
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

""" Forms for Resources application """

from django import forms
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from esp.resources.models import ResourceType, ResourceRequest, NewResourceType, AbstractResource, NewResource, NewResourceRequest
from esp.tagdict.models import Tag
from validators import ExactlyOneNotEmptyValidator

class IDBasedModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return "%d" % obj.id

class ResourceRequestForm(forms.Form):
    resource_type = IDBasedModelChoiceField(queryset=ResourceType.objects.all(), widget=forms.HiddenInput)
    desired_value = forms.ChoiceField(choices=(), widget=forms.RadioSelect, required=False)
    #   desired_value = forms.ChoiceField(choices=())
    
    def __init__(self, data=None, **kwargs):
    
        if 'resource_type' in kwargs:
            self.resource_type = kwargs['resource_type']
            del kwargs['resource_type']

        super(ResourceRequestForm, self).__init__(data, **kwargs)
    
        if data and ('prefix' in kwargs):
            self.prefix = kwargs['prefix']
            key_name = self.add_prefix('resource_type')
            if key_name in data:
                self.resource_type = ResourceType.objects.get(id=data[key_name])
            
        if hasattr(self, 'resource_type'):
            self.fields['desired_value'].label = self.resource_type.name
            #   If this is the only form to be displayed, show all options as checkboxes and let the user pick
            #   any number (or none) with this form
            if self.resource_type.only_one:
                pass
            else:
                self.fields['desired_value'] = forms.MultipleChoiceField(choices=(), widget=forms.CheckboxSelectMultiple, required=False)
                self.fields['desired_value'].label = self.resource_type.name
            #   Don't provide a blank default value
            #   self.fields['desired_value'].choices = zip(tuple(' ') + self.resource_type.choices, tuple(' ') + self.resource_type.choices)    
            self.fields['desired_value'].choices = zip(self.resource_type.choices, self.resource_type.choices)
            
            self.initial['resource_type'] = self.resource_type.id

        
class ResourceRequestFormSet(formset_factory(ResourceRequestForm, extra=0)):
    """ Like a FormSet, but handles the list of resource_types for the forms to start out with. """
    def __init__(self, *args, **kwargs):
        if 'resource_type' in kwargs:
            self.resource_type = kwargs['resource_type']
            del kwargs['resource_type']
        super(ResourceRequestFormSet, self).__init__(*args, **kwargs)
    
    def initial_form_count(self):
        """Returns the number of forms that are required in this FormSet."""
        if hasattr(self, 'resource_type'):
            return len(self.resource_type)
        else:
            return super(ResourceRequestFormSet, self).initial_form_count()
    
    def _construct_form(self, i, **kwargs):
        #   Adapted from Django 1.1 release.
        """
        Instantiates and returns the i-th form instance in a formset.
        """
        defaults = {'auto_id': self.auto_id, 'prefix': self.add_prefix(i)}
        if self.data or self.files:
            defaults['data'] = self.data
            defaults['files'] = self.files
        if self.initial:
            try:
                defaults['initial'] = self.initial[i]
            except IndexError:
                pass
        # Allow extra forms to be empty.
        if i >= self.initial_form_count():
            defaults['empty_permitted'] = True
            
        #   Update by Michael Price for resource requests (app specific)
        default_args = kwargs.copy()
        if hasattr(self, 'resource_type'):
            #   Select out appropriate list item for the form being constructed.
            if type(self.resource_type) == list:
                default_args['resource_type'] = self.resource_type[i]
            
        defaults.update(default_args)
        form = self.form(**defaults)
        self.add_fields(form, i)
        
        return form
    
class ResourceTypeForm(forms.ModelForm):
    name = forms.CharField(label='New Request', required=False)

    class Meta:
        model = ResourceType
        fields = ['name']
    
class ResourceTypeFormSet(formset_factory(ResourceTypeForm, extra=0)):
    pass

class NewResourceForm(forms.ModelForm):
    class Meta:
        model = NewResource
        exclude = ['availability', 'abstraction']
        widgets = {
                'description': forms.Textarea(attrs={'rows': 2}),
                }

NewResourceFormSet = modelformset_factory(NewResource, form=NewResourceForm, extra=5)

class AbstractResourceForm(forms.ModelForm):
    class Meta:
        model = AbstractResource
        fields = ['resource_type', 'name', 'is_active', 'is_reusable', 'is_requestable', 'description']
        widgets = {
                'resource_type': forms.HiddenInput(),
                'is_active': forms.HiddenInput(),
                'description': forms.Textarea(attrs={'cols': 30}),
                }

class NewResourceTypeForm(forms.ModelForm):
    class Meta:
        model = NewResourceType
        fields = ['parent', 'name', 'is_active', 'is_reusable', 'is_requestable', 'is_substitutable', 'description']
        widgets = {
                'parent': forms.HiddenInput(),
                'is_active': forms.HiddenInput(),
                'description': forms.Textarea(attrs={'cols': 30}),
                }

class AmountOrPercentField(forms.IntegerField):
    """
    A Django form field that can take either an amount or an integer percentage.
    An amount is entered as it would be in an IntegerField.
    A percentage is entered with a trailing '%' character.
    In both cases, the IntegerField value cleaning and validating is performed
    on the integer part of the input.
    """
    def __init__(self, amount_field_name=None, pcnt_field_name=None,
                 max_amount=None, min_amount=0,
                 max_percent=None, min_percent=0, *args, **kwargs):
        """
        Separate bounds can be placed on amounts and percentages.
        The default is for both to be restricted to non-negative values.
        The max_value / min_value parameters of the parent class are explicitly
        forbidden from being passed, since this would be ambiguous.

        Accepts amount_field_name and pcnt_field_name parameters, to record
        the two underlying field names.

        Instances of this field have an is_percent attribute, which records
        whether or not the value should be treated as a percentage or not. The
        default is to assume that it is not a percentage, but an amount.
        """
        assert ('max_value' not in kwargs) and ('min_value' not in kwargs)
        self.amount_field_name, self.pcnt_field_name = amount_field_name, pcnt_field_name
        self.max_amount, self.min_amount = max_amount, min_amount
        self.max_percent, self.min_percent = max_percent, min_percent
        self.is_percent = False
        super(AmountOrPercentField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, basestring):
            value = value.strip()
        if isinstance(value, basestring) and len(value)>0 and value[-1]=='%':
            self.is_percent = True
            if self.max_percent is not None:
                self.validators.append(MaxValueValidator(self.max_percent))
            if self.min_percent is not None:
                self.validators.append(MinValueValidator(self.min_percent))
            value = value[:-1]
        else:
            if self.max_amount is not None:
                self.validators.append(MaxValueValidator(self.max_amount))
            if self.min_amount is not None:
                self.validators.append(MinValueValidator(self.min_amount))
        return super(AmountOrPercentField, self).to_python(value)

    def clean_fields(self, value, cleaned_data):
        """
        Given the cleaned value of this field, sets it as the cleaned value of
        either the amount field or the percent field, depending on
        self.is_percent.

        Requires that the amount_field_name and pcnt_field_name attributes
        were set during initialization.

        Should be called by the form's clean() method.
        """
        assert self.amount_field_name and self.pcnt_field_name
        if self.is_percent:
            cleaned_data[self.pcnt_field_name] = value
            cleaned_data[self.amount_field_name] = None
        else:
            cleaned_data[self.amount_field_name] = value
            cleaned_data[self.pcnt_field_name] = None

class NewResourceRequestForm(forms.ModelForm):
    amount_or_pcnt_of_capacity = AmountOrPercentField('amount', 'pcnt_of_capacity', initial=1, label='Amount or percent of capacity', help_text="Enter either the amount of this resource that you want as a whole number of objects, or as a percentage of the final capacity of your class (as an integer followed by a '%' character).")
    class Meta:
        model = NewResourceRequest
        fields = ['resource_content_type', 'resource_object_id', 'subject', 'amount_or_pcnt_of_capacity', 'amount', 'pcnt_of_capacity', 'required', 'description']
        exclude = ['wont_satisfy', 'is_satisfied_override']
        widgets = {
#            'resource_content_type': forms.HiddenInput,
#            'resource_object_id': forms.HiddenInput,
#            'subject': forms.HiddenInput,
            'amount': forms.HiddenInput,
            'pcnt_of_capacity': forms.HiddenInput,
            'description': forms.Textarea(attrs={'rows': 4})
        }

    def __init__(self, *args, **kwargs):
        super(NewResourceRequestForm, self).__init__(*args, **kwargs)
        self.amount_or_pcnt_of_capacity_validator = ExactlyOneNotEmptyValidator(dict([(name, self.fields[name].label) for name in ['amount', 'pcnt_of_capacity']]))

    def clean(self):
        cleaned_data = super(NewResourceRequestForm, self).clean()
        amount_or_pcnt_value = cleaned_data.get('amount_or_pcnt_of_capacity', None)
        self.fields['amount_or_pcnt_of_capacity'].clean_fields(amount_or_pcnt_value, cleaned_data)
        try:
            self.amount_or_pcnt_of_capacity_validator(cleaned_data['amount'], cleaned_data['pcnt_of_capacity'])
        except ValidationError, e:
            del cleaned_data['amount']
            del cleaned_data['pcnt_of_capacity']
            self._errors = e.update_error_dict(self._errors)
        return cleaned_data

    def as_table(self):
        "Returns this form rendered as HTML <tr>s -- excluding the <table></table>."
        return self._html_output(
            normal_row = u'<tr%(html_class_attr)s><th>%(label)s</th><td>%(field)s%(help_text)s%(errors)s</td></tr>',
            error_row = u'<tr><td colspan="2">%s</td></tr>',
            row_ender = u'</td></tr>',
            help_text_html = u'<br /><span class="helptext">%s</span>',
            errors_on_separate_row = False)

