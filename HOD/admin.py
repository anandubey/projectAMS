from django.contrib import admin
from .models import Course, Course_allot, Hod_credential, Semester_wise_course, Semester_wise_electives

admin.site.register(Semester_wise_course)
admin.site.register(Semester_wise_electives)
admin.site.register(Course_allot)
admin.site.register(Course)
admin.site.register(Hod_credential)
