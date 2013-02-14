from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, Http404, HttpResponseServerError
from django.views.decorators.http import require_POST

from esp.program.models import Program, ClassSubject
from esp.users.models import admin_required, ESPUser

import gspread
import json
import os
import re

# Columns in the Accounting spreadsheet, one-indexed
AC_DATE         = 1
AC_AMOUNT       = 2
AC_USERNAME     = 3
AC_CODE         = 4
AC_RFP_STATUS   = 5
AC_CATEGORY     = 6
AC_DESCRIPTION  = 7
AC_NOTES        = 8

ACCOUNTING_HEADER = "Date"  # header row, first column

# Columns in the Budget spreadsheet, one-indexed
BC_CATEGORY     = 1
BC_SUBCATEGORY  = 2
BC_QUANTITY     = 3
BC_UNIT_REV     = 4
BC_TOTAL_REV    = 5
BC_COMMENTS     = 6

BUDGET_HEADER = "Category"



@admin_required
def check_auth(request):
    return HttpResponse("SAPmonkey connected! " + request.COOKIES['csrftoken'])

@admin_required
def lookup_username(request, username):
    result = ESPUser.objects.filter(username=username)
    if len(result) == 0:
        result = ESPUser.objects.filter(username__iexact=username)
        if len(result) != 1:
            raise Http404()
    
    elif len(result) > 1:
        raise Http404()
    
    user = result[0]
    isMIT = user.email.strip().endswith("@mit.edu")
    
    response_data = {'isMIT': isMIT, 'name': user.name(), 'username': user.username}
    return HttpResponse(json.dumps(response_data), mimetype='application/json')

@admin_required
def list_budget_categories(request):
    f = open(os.path.join(settings.PROJECT_ROOT, 'esp', 'sapmonkey', 'categories.cache'), 'r')
    data = f.read()
    f.close()
    return HttpResponse(data, mimetype='application/json')

@admin_required
def save_budget_categories(request):
    gc = gspread.login(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
    spreadsheet = gc.open_by_key(settings.BUDGET_SPREADSHEET_KEY)
    worksheets = spreadsheet.worksheets()
    
    response_data = dict()
    response_data['programs'] = list()
    response_data['categories'] = dict()
    
    # Insert extra budgets (e.x., for past programs, etc.)
    #  These go in Miscellaneous
    for c in settings.EXTRA_BUDGETS:
        response_data['programs'].append(c)
    
    # Iterate over each worksheet (i.e., each program's budget)
    for w in worksheets:
        budget_categories = list()
        
        # Find out how many rows are in the header (about 6)
        header_row = find_header_row(w, BUDGET_HEADER)
        if header_row is None:
            return HttpResponseServerError(
                'No header row found - looking for "' + BUDGET_HEADER +
                '" in column A of ' + w.title)
        
        # Get contents of worksheet
        categories = w.col_values(BC_CATEGORY)
        subcategories = w.col_values(BC_SUBCATEGORY)
        
        # Iterate over the rows to list categories in the format
        #   "Big Category - Detailed Category" (i.e., "Publicity - Booth Candy")
        #
        # Direction: right-to-left, top-to-bottom
        # Note that items in Column 1 that contain '$' are subtotals, not
        #   categories, and are skipped
        category = "None"
        for n in range(header_row, w.row_count):
            # n is a zero-based index, header_row is one-based.
            # skip the header.
            
            if (n < len(categories)
                and categories[n]
                and not '$' in categories[n]):   # cells with a '$' are subtotals
                
                category = categories[n]
            
            if n < len(subcategories) and subcategories[n]:
                
                item = category + ' - ' + subcategories[n]
                budget_categories.append(item)
        
        response_data['programs'].append(w.title)
        response_data['categories'][w.title] = budget_categories
    
    f = open(os.path.join(settings.PROJECT_ROOT, 'esp', 'sapmonkey', 'categories.cache'), 'w')
    f.write(json.dumps(response_data))
    f.close()
    
    return HttpResponse("Saved")

@admin_required
def list_classes(request, program, select, username):
    pr = find_program(program)
    if not pr:
        raise Http404("Program not found")
    
    response_data = dict()
    response_data['program'] = program
    response_data['classes'] = list()
    
    if select == 'all':
        results = ClassSubject.objects.filter(parent_program=pr).order_by('id')
        for cs in results:
            response_data['classes'].append(format_class(cs))
    
    elif select == 'only':
        users = ESPUser.objects.filter(username=username)
        
        if len(users) != 1:
            raise Http404("Username not found")
            
        results = users[0].getTaughtClassesFromProgram(pr).order_by('id')
        for cs in results:
            response_data['classes'].append(format_class(cs))
    
    elif select == 'priority':
        users = ESPUser.objects.filter(username=username)
        
        if len(users) != 1:
            raise Http404("Username not found")
        
        results = users[0].getTaughtClassesFromProgram(pr).order_by('id')
        for cs in results:
            response_data['classes'].append(format_class(cs))
        
        full_results = ClassSubject.objects.filter(
            parent_program=pr).order_by('id')
        for cs in full_results:
            if cs not in results:
                response_data['classes'].append(format_class(cs))
    
    else:
        raise Http404("Unknown option")
    
    return HttpResponse(json.dumps(response_data), mimetype='application/json')

@admin_required
@require_POST
def save_rfp(request):
    data = json.loads(request.REQUEST['data'])
    
    gc = gspread.login(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
    spreadsheet = gc.open_by_key(settings.ACCOUNTING_SPREADSHEET_KEY)
    worksheets = spreadsheet.worksheets()
    
    # Put each line item into the budget spreadsheet
    for n in range(0, len(data['line_items'])):
        item = data['line_items'][str(n)]
        
        # Find which worksheet (i.e., program/office) matches
        name = item['program']
        name = re.sub('\s*' + str(settings.FISCAL_YEAR) + '\s*', '', name)  # remove year, if present
        name = name.lower() # case-insentitive compare
        
        # Check for program "Miscellaneous/Other"
        if name == "miscellaneous/other":
            name = "miscellaneous"
        
        w = None
        for tmp in worksheets:
            if name == tmp.title.lower():
                w = tmp
                break
        
        if w is None:
            raise Http404("No program found that matches: " + item['program'])
        
        header_row = find_header_row(w, ACCOUNTING_HEADER)
        
        # Check that the RFP hasn't already been entered
        existing_codes = w.col_values(AC_CODE)
        for n in range(header_row, len(existing_codes)):
            if (existing_codes[n] is not None and
                data['rfp_number'] in existing_codes[n]):
                
                return HttpResponseServerError("RFP already exists")
        
        # Insert RFP into spreadsheet
        
        row = len(w.get_all_values()) + 1
          # get_all_values() leaves off the blank rows at the bottom;
          # this returns the one-indexed number of the row *after*
          # the last row with anything in it - this is where we'll
          # put the new data
        
        code = 'RFP-' + data['rfp_number']
        if len(data['line_items']) > 1:
            code = code + '-' + str(n+1)
        
        desc = ''
        if 'class' in item:
            desc = item['class']
        elif 'description' in item:
            desc = item['description']
        
        addr = 'A%s:H%s' % (row, row)
        cells = w.range(addr)
        cells[AC_DATE-1].value          = item['date']
          # switch from one-indexed AC_* constants to zero-indexed list
        cells[AC_AMOUNT-1].value        = item['amount']
        cells[AC_USERNAME-1].value      = data['esp_username']
        cells[AC_CODE-1].value          = code
        cells[AC_RFP_STATUS-1].value    = 'Unreviewed'
        cells[AC_CATEGORY-1].value      = item['budget_category']
        cells[AC_DESCRIPTION-1].value   = desc
        cells[AC_NOTES-1].value         = ''
        w.update_cells(cells)
        
    return HttpResponse()

@admin_required
def view_rfp(request, number):
    gc = gspread.login(settings.GOOGLE_USERNAME, settings.GOOGLE_PASSWORD)
    spreadsheet = gc.open_by_key(settings.ACCOUNTING_SPREADSHEET_KEY)
    worksheets = spreadsheet.worksheets()
    
    response_data = dict()
    response_data['warnings'] = list()
    
    code = 'RFP-' + number
    for w in worksheets:
        nums = w.col_values(AC_CODE)
        
        for i in range(0, len(nums)):
            if nums[i] is None:
                continue
            
            if code not in nums[i]:
                continue
            
            line = 'line-1'
            
            parts = nums[i].split('-')
            if len(parts) == 3:
               line = 'line-' + parts[2]
            
            if line in response_data:
                response_data['warnings'].append('Duplicate line items in spreadsheet: ' + w.title + ' row ' + str(i + 1)
                    + ' and ' + response_data[line]['ssid'])
                continue
            
            row = w.row_values(i + 1)
            response_data[line] = dict()
            response_data[line]['ssid'] = w.title + ' row ' + str(i + 1)
            response_data[line]['program'] = w.title
            if len(row) > AC_DATE - 1:
                response_data[line]['date'] = row[AC_DATE - 1]    # 0/1 index
            if len(row) > AC_AMOUNT - 1:
                response_data[line]['amount'] = row[AC_AMOUNT - 1]
            if len(row) > AC_USERNAME - 1:
                response_data[line]['username'] = row[AC_USERNAME - 1]
            if len(row) > AC_RFP_STATUS - 1:
                response_data[line]['status'] = row[AC_RFP_STATUS - 1]
            if len(row) > AC_CATEGORY - 1:
                response_data[line]['category'] = row[AC_CATEGORY - 1]
            if len(row) > AC_DESCRIPTION - 1:
                response_data[line]['description'] = row[AC_DESCRIPTION - 1]
            if len(row) > AC_NOTES - 1:
                response_data[line]['notes'] = row[AC_NOTES - 1]
    
    if len(response_data) == 1:
        raise Http404()
    
    return HttpResponse(json.dumps(response_data), mimetype='application/json')



def find_header_row(worksheet, first_column_header):
    column = worksheet.col_values(1)
    for n in range(0, worksheet.row_count):
        if column[n] == first_column_header:
            return n + 1  # zero-indexed list, one-indexed sheet
    return None

def find_program(search):
    # Append the current year, if not included
    if not re.search('\d{4}', search):
        search += ' ' + str(settings.FISCAL_YEAR)
    
    # Given a string such as "Spring HSSP 2013", finds the corresponding program
    parts = search.split()
    
    # Find all programs where the parent type (e.g., "HSSP") and the friendly
    # name (e.g., "Spring 2013") both contain parts of the search text
    qParent = Q()
    qChild = Q()
    for p in parts:
        qParent = qParent | Q(anchor__parent__friendly_name__contains=p)
        qChild = qChild | Q(anchor__friendly_name__contains=p)
    
    # Find the first program that contains all parts of the search text
    results = Program.objects.filter(qParent, qChild)
    for r in results:
        names = r.niceName().split()
        i = 0
        for p in parts:
            for n in names:
                if p in n:
                    i += 1
                    break
        
        if i == len(parts):
            return r
    
    return None

def format_class(cs):
    name = ""
    
    symbol = cs.category.symbol
    if symbol:
        name += symbol
    
    name += str(cs.id)
    
    title = cs.title()
    if title:
        name += ': ' + title
    
    return name
