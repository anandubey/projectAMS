from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date
from .models import FacultyProfile, attendance
from student.models import StudentProfile
from HOD.models import Course_allot


def faculty(request):
    if not request.session.get('logged'):
        return redirect('home')
    if request.session.get('hod_logged'):
        return redirect('hod_index')
    username = request.session.get('username')
    if len(username) == 10:
        return redirect('student')
    
    else:
        faculty = FacultyProfile.objects.get(faculty_id=username)
        return render(request, 'faculty/faculty-home.html', {'user_instance': faculty})

def update_attend(request):
    if not request.session.get('logged'):
        return redirect('home')
    if request.session.get('hod_logged'):
        return redirect('hod_index')
    username = request.session.get('username')
    if len(username) == 10:
        return redirect('student')
    faculty = FacultyProfile.objects.get(faculty_id=username)

    if request.method == "POST":
        if 'att_filter_btn' in request.POST:
            batch = request.POST.get('select_batch')
            department = request.POST.get('select_department')
            course_code = request.POST.get('select_course_code')
            selected_date = request.POST.get('att_date')
 
            user_set = StudentProfile.objects.filter(reg_no__startswith=batch, department=department)
            filters = _get_filters(username=username, selected_batch=batch, selected_department=department, selected_course=course_code)
            filters['selected_date'] = selected_date
            filters['selected_course'] = course_code
            return render(request, 'faculty/update_attend.html', {'user_instance': faculty, 'filters':filters,'user_set': user_set})
        
        elif 'att_data_submit_btn' in request.POST:
            _save_attendance_data(request.POST)
            course_code = request.POST.get('course_code')
            selected_date = request.POST.get('attendance_date')
            d = tuple(map(int,selected_date.split('-')))
            out_date = date(d[0],d[1],d[2]).strftime('%d %b %Y')
            msg = 'Attendance updated for ' + course_code + ' on ' + out_date
            messages.success(request,msg)
            return redirect('update_attend')
    else:
        filters = _get_filters(username=username)
        return render(request, 'faculty/update_attend.html', {'user_instance': faculty, 'filters':filters,'user_set': {}})

def faculty_logout(request):
    request.session.clear()
    return redirect('home')

""" Custom functions below here """

def _get_filters(username=None, selected_batch=None, selected_department=None, selected_course=None):
    if username is None:
        return dict()
    allotted_courses = Course_allot.objects.filter(faculty_id=username).values('year', 'department', 'course_code')
    courses = list()
    batches = list()
    departments = list()
    for course in allotted_courses:
        batch = course.get('year')
        if batch == selected_batch:
            this_batch = {'year':batch, 'checked':True}
        else:
            this_batch = {'year':batch, 'checked':False}
        if this_batch not in batches:
            batches.append(this_batch)

        course_code = course.get('course_code')
        if course_code == selected_course:
            courses.append({'course_code':course_code, 'checked':True})
        else:
            courses.append({'course_code':course_code, 'checked':False})

        department = course.get('department')
        if department == selected_department:
            this_dep = {'department':department, 'checked':True}
        else:
            this_dep = {'department':department, 'checked':False}
        if this_dep not in departments:
            departments.append(this_dep)
    
    attendance_filters = {'courses':courses, 'batches':batches, 'departments':departments}
    return attendance_filters


def _save_attendance_data(post_array):
    date = post_array.get('attendance_date')
    course_code = post_array.get('course_code')
    print('COURSE CODE',course_code)
    for key, value in post_array.items():
        if key.startswith('reg_'):
            stu_inst = StudentProfile.objects.get(reg_no=key[4:])
            if stu_inst is not None:
                attend_instance = attendance.objects.create(reg_no=stu_inst, date=date, course_code=course_code, attendance=value, if_mod=False)
                attend_instance.save()
        
            