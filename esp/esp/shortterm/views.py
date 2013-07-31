# Create your views here.

from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from esp.web.util.main import render_to_response
from esp.users.models import admin_required
from esp.shortterm.models import ResponseForm
from esp.shortterm.crazy_excel_thing import build_workbook

class SchoolResponseForm(forms.ModelForm):
    class Meta:
        model = ResponseForm

def school_response_form(request):
    if request.POST:
        response = SchoolResponseForm(request.POST)
        if response.is_valid():
            data = response.save()
            data.send_mail()
            return HttpResponseRedirect("/school_response/thanks.html")

    else:
        response = SchoolResponseForm()

    return render_to_response("shortterm/school_response/form.html", request, context={ 'form': response })

@admin_required
def excel_survey_responses(request):
    response = HttpResponse(build_workbook().getvalue(), mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=esp-survey-results-all.xls'
    return response

@login_required
def logistics_quiz_check(request):
    from esp.middleware import ESPError
    from esp.users.models import UserBit
    from esp.datatree.models import GetNode

    def _back():
        return HttpResponseRedirect("/teach/Spark/quiz.html")
    def _fail():
        return HttpResponseRedirect("/teach/Spark/quiz_tryagain.html")
    correct_answers = {
        'prog_month': '3',
        'prog_day': '13',
        'photo_exists': 'False',
        'call_911': 'False',
        'teacher_lunch': 'True',
        'check_in': 'True',
    }
    checkboxes = {
        'sec1': True,
        'sec2': False,
        'sec3': True,
        'sec4': True,
        'sec5': True,
        'sec6': True,
        
        'reimburse1': True,
        'reimburse2': False,
        'reimburse3': False,
        'reimburse4': True,
    }
    
    if not request.POST or not request.user.isTeacher():
        return _back()
    
    for key in correct_answers:
        if request.POST.get(key, '') != correct_answers[key]:
            return _fail(key)
    for key in checkboxes:
        if bool(request.POST.get(key, False)) != checkboxes[key]:
            return _fail(key)
    ans = request.POST.get('security_number', '')
    if ''.join([x for x in ans if x.isdigit()]) != '6172534941':
        return _fail()
    
    first_class = request.user.getTaughtSections().filter(parent_class__parent_program=18, status=10).order_by('meeting_times') or [None]
    first_class = first_class[0]
    if first_class is None:
        raise ESPError(False), "You don't have any classes scheduled! Please talk to the directors."
    else:
        ans = request.POST.get('room_number', '')
        if ans.strip() not in first_class.prettyrooms():
            return _fail()
        ans = request.POST.get('first_class')
        if ans == first_class.meeting_times.order_by('start')[0].start.hour:
            return _fail()
    
    ub, created = UserBit.objects.get_or_create(user=request.user, qsc=GetNode('Q/Programs/Spark/2010'), verb=GetNode('V/Flags/Registration/Teacher/QuizDone'))
    if not created:
        ub.renew()
    return HttpResponseRedirect("/teach/Spark/quiz_success.html")
