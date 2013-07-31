from esp.program.models import Program, StudentRegistration, ClassSection
from esp.users.models import ESPUser
from esp.users.models.userbits import UserBit
from esp.datatree.models import GetNode
from datetime import datetime, timedelta, date, time
from django.db.models.aggregates import Min

# Spark 2013
prog = Program.objects.get(id=88)
# classes that started more than 120 minutes ago
passed_sections = prog.sections().annotate(begin_time=Min("meeting_times__start")).filter(status=10, parent_class__status=10, begin_time__start__lt=datetime.now() - timedelta(minutes=120), begin_time__start__gt = datetime.combine(date.today(), time(0, 0)))
# students who are enrolled in a class that started more than 120 minutes ago, who have not checked in
#students = ESPUser.objects.filter(studentregistration__in=StudentRegistration.valid_objects(), studentregistration__relationship=1, studentregistration__section__in=passed_sections).distinct().exclude(userbit__in=UserBit.valid_objects(), userbit__qsc=prog.anchor, userbit__verb=GetNode('V/Flags/Registration/Attended'))
all_students = ESPUser.objects.filter(studentregistration__in=StudentRegistration.valid_objects(), studentregistration__relationship=1, studentregistration__section__in=passed_sections).distinct()
students = set(all_students) - set(all_students.filter(userbit__in=UserBit.valid_objects(), userbit__qsc=prog.anchor, userbit__verb=GetNode('V/Flags/Registration/Attended')))
# classes that start today
upcoming_sections = prog.sections().annotate(begin_time=Min("meeting_times__start")).filter(status=10, parent_class__status=10, begin_time__start__gt=datetime.now(), begin_time__start__lt=datetime.combine(date.today(), time(23, 59)))
# registrations of missing students for upcoming classes
registrations = StudentRegistration.valid_objects().filter(user__in=students, section__in=upcoming_sections, relationship=1)
# filter out materials-intensive classes
registrations = registrations.exclude(section__parent_class__id__in=[6866,6914,6926,6927,6932,6943,6948,6958,6970,6971,6993,7006,7009,7021,7191,7187,7186,7026,7030,7180,7178,7047,7168,7050,7051,7056,7059,7164,7060,7161,7063,7156,7151,7150,7146,7144,7141,7064,7077,7137,7082,7135,7127,7123,7117,7104,7102,7098,7097,7089,7088,7087,7083])
registrations.update(end_date=datetime.now())
print list(registrations)
