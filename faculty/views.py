from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date
from .models import FacultyProfile, attendance
from student.models import StudentProfile
from HOD.models import Course_allot


def faculty(request):
    if not request.session.get('logged'):
        return redirect('home')
    user_type = request.session.get('user_type')
    if user_type != 'faculty':
        return redirect('home')
    
    username = request.session.get('username')
    faculty = FacultyProfile.objects.get(faculty_id=username)
    return render(request, 'faculty/faculty-home.html', {'user_instance': faculty})


def update_attend(request):
    if not request.session.get('logged'):
        return redirect('home')
    user_type = request.session.get('user_type')
    if user_type != 'faculty':
        return redirect('home')

    username = request.session.get('username')
    faculty = FacultyProfile.objects.get(faculty_id=username)

    if request.method == "POST":
        if 'att_filter_btn' in request.POST:
            batch = request.POST.get('select_batch')
            department = request.POST.get('select_department')
            course_code = request.POST.get('select_course_code')
            selected_date = request.POST.get('att_date')
            user_set = None
            date_exist = False
            if not attendance.objects.filter(date=selected_date).exists():
                user_set = StudentProfile.objects.filter(reg_no__startswith=batch, department=department)
            else:
                date_exist = True
            filters = _get_filters(username=username, selected_batch=batch, selected_department=department, selected_course=course_code)
            filters['selected_date'] = selected_date
            filters['selected_course'] = course_code
            return render(request, 'faculty/update_attend.html', {'user_instance': faculty, 'filters':filters,'user_set': user_set, 'date_exist':date_exist})
        
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


def view_attend(request):
    if not request.session.get('logged'):
        return redirect('home')
    user_type = request.session.get('user_type')
    if user_type != 'faculty':
        return redirect('home')

    username = request.session.get('username')
    if request.method == 'GET':
        faculty = FacultyProfile.objects.get(faculty_id=username)
        return render(request, 'faculty/view_attend.html', {'filters': _get_historical_course_filter(username=username), 'freshpage':True} )
    else:
        faculty = FacultyProfile.objects.get(faculty_id=username)
        
        selected_year = request.POST.get('select_year')

        selected_semester = request.POST.get('select_semester')
        selected_semester = None if (selected_semester == '' or selected_semester is None) else int(selected_semester)

        selected_course = request.POST.get('select_course_code')
        selected_course = None if selected_course == '' else selected_course

        filters = _get_historical_course_filter(username=username, selected_year=selected_year, selected_semester=selected_semester, selected_course=selected_course)
        if selected_course is None:
            return render(request, 'faculty/view_attend.html', {'filters': filters})
        else:
            attendance_list = _get_attendance_data_for_course(selected_course)
            return render(request, 'faculty/view_attend.html', {'filters': filters, 'attendance':attendance_list})



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


def _get_historical_course_filter(username=None, selected_year=None, selected_semester=None, selected_course=None):
    if username is None:
        return dict()
    else:
        try:
            allotted_courses = list(Course_allot.objects.filter(faculty_id=username).values('year', 'course_code', 'semester').distinct())
            courses = list()
            years = list()
            semesters = list()

            for course in allotted_courses:
                year = course.get('year')
                if year == selected_year:
                    this_year = {'value':year, 'checked':True}
                else:
                    this_year = {'value':year, 'checked':False}
                if this_year not in years:
                    years.append(this_year)

                if selected_year is not None:
                    semester = course.get('semester')
                    if semester == selected_semester:
                        this_sem = {'value':semester, 'checked':True}
                    else:
                        this_sem = {'value':semester, 'checked':False}
                    if this_sem not in semesters:
                        semesters.append(this_sem)

                if  selected_semester is not None:
                    course_code = course.get('course_code')
                    if course_code == selected_course:
                        courses.append({'course_code':course_code, 'checked':True})
                    else:
                        courses.append({'course_code':course_code, 'checked':False})

            attendance_filters = {'courses':courses, 'years':years, 'semesters':semesters}
            return attendance_filters

        except Course_allot.DoesNotExist:
            return dict()


def _get_attendance_data_for_course(course_code):
    try:
        students = list(attendance.objects.filter(course_code=course_code).values_list('reg_no', flat=True).distinct().order_by('reg_no'))
    except attendance.DoesNotExist:
        return dict()
    attendance_data = dict()
    student_attendance_list = []
    max_classes = 0
    for reg_no in students:
        total = attendance.objects.filter(reg_no=reg_no, course_code=course_code).count()
        present = attendance.objects.filter(reg_no=reg_no, course_code=course_code, attendance='P').count()
        if total != 0:
            nocourse = False
            if total > max_classes:
                max_classes = total
        student_attendance_list.append({'reg_no':reg_no, 'present':present})

    attendance_data['total'] = max_classes
    attendance_data['students'] = student_attendance_list

    return attendance_data
