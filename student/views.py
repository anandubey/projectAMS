from django.shortcuts import render, redirect
from .models import StudentProfile
from faculty.models import attendance
from HOD.models import Semester_wise_course
from datetime import date

def student(request):
    username = request.session.get('username')
    if username is not None:
        user_instance = StudentProfile.objects.get(reg_no=username)
        department = user_instance.department
        this_semester = (date.today().year - int(username[:4]))*2
        if date.today().month >= 7:
            this_semester += 1
        courses = Semester_wise_course.objects.get(department=department, semester=this_semester).courses.split('-')
        att_data_list = []                                         # using list of dictionaries to store attendance 
        for course_code in courses:
            total = attendance.objects.filter(reg_no=user_instance, course_code=course_code).count()
            present = attendance.objects.filter(reg_no=user_instance, course_code=course_code, attendance='P').count()
            if total != 0:
                percent_present = (present/total)*100
            else:
                percent_present = 100
            less_attendance = False
            if percent_present < 75:
                less_attendance = True
            att_data = {'course_code':course_code, 'total_classes':total, 'attended':present, 'percent':percent_present, 'less_attend':less_attendance}
            att_data_list.append(att_data)
        return render(request, 'student/student-home.html', {'user_instance': user_instance, 'att_data_list': att_data_list, 'stu_sem':this_semester })
    else:
        return redirect('home')


def student_logout(request):
    request.session.clear()
    return redirect('home')