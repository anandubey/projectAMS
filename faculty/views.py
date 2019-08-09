from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import F, Sum
from datetime import date
from .models import FacultyProfile, attendance
from student.models import StudentProfile
from HOD.models import Course_allot, Course, Hod_credential


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
            if not attendance.objects.filter(date=selected_date,course_code=course_code).exists():
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
        
        selected_batch = request.POST.get('select_batch')
        selected_semester = request.POST.get('select_semester')
        selected_semester = None if (selected_semester == '' or selected_semester is None) else int(selected_semester)
        selected_dep = request.POST.get('dep_code')
        selected_dep = None if selected_dep == '' else selected_dep
        selected_course = request.POST.get('select_course_code')
        selected_course = None if selected_course == '' else selected_course

        filters = _get_historical_course_filter(username=username, selected_batch=selected_batch, selected_semester=selected_semester, selected_course=selected_course, selected_dep=selected_dep)
        if selected_course is None:
            return render(request, 'faculty/view_attend.html', {'filters': filters})
        else:
            attendance_list = _get_attendance_data_for_course(selected_course, selected_batch, selected_dep)
            return render(request, 'faculty/view_attend.html', {'filters': filters, 'attendance':attendance_list})


def attendance_report(request):
    if not request.session.get('logged'):
        return redirect('home')
    user_type = request.session.get('user_type')
    if user_type != 'faculty':
        return redirect('home')

    faculty_id = request.session.get('username')
    courses = _get_courses_for_report(faculty_id)
    if request.method == 'POST':
        is_inadequacy = request.POST.get('is_inadequacy',None)
        course_dep_year = request.POST.get('course_code').split('_')
        course_code = course_dep_year[0]
        department = course_dep_year[1]
        year = course_dep_year[2]
        if is_inadequacy is not None:
            inadequacy = True
        else:
            inadequacy = False
        report_data = dict()
        report_data['year'] = year
        report_data['course'] = course_code
        report_data['department'] = department
        report_data['inadequacy'] = inadequacy
        report_data['is_ready'] = True
        return render(request, 'faculty/filter_attendance_report.html',{'course_filter':courses, 'report_data':report_data})
    else:
        return render(request, 'faculty/filter_attendance_report.html',{'course_filter':courses})


def generate_report(request):
    if request.method == 'POST':
        course_code = request.POST.get('report_course_code')
        course_title = Course.objects.get(course_code=course_code).title
        dep = request.POST.get('report_department').upper()
        department_code = _depcode(dep)
        dep_full_name = _dep_full_name(dep)
        batch = request.POST.get('report_course_year')
        hod_id = Hod_credential.objects.get(department=dep).hod_id
        hod_name = FacultyProfile.objects.get(faculty_id=hod_id).name
        faculty_name = FacultyProfile.objects.get(faculty_id=request.session.get('username')).name
        inadequacy = True if request.POST.get('report_is_inadequacy') == 'True' else False
        this_semester = (date.today().year - int(batch))*2
        if date.today().month >= 7:
            this_semester += 1
        
        attendance_data = _get_attendance_data_for_course(course_code.upper(), batch, department_code, inadequacy=inadequacy)
        max_date = date.today().strftime('%d-%m-%Y')

        final_report = dict()
        final_report['inadequacy'] = inadequacy
        final_report['semester'] = this_semester
        final_report['date_upto'] = max_date
        final_report['course_code'] = course_code
        final_report['course_title'] = course_title
        final_report['hod_name'] = hod_name
        final_report['faculty_name'] = faculty_name
        final_report['department_full_name'] = dep_full_name
        final_report['total_classes'] = attendance_data.get('total')
        students_list = list()
        
        for key in attendance_data.get('students'):
            reg_no = key.get('reg_no')
            classes_attended = key.get('present')
            name = StudentProfile.objects.get(reg_no=reg_no).name
            students_list.append({'name':name, 'reg_no':reg_no, 'present':classes_attended})
        
        final_report['students'] = students_list
        return render(request, 'faculty/attendance_report.html', {'report':final_report})
    else:
        return render(request, 'faculty/attendance_report.html', {})


def lesson_plan(request):
    if not request.session.get('logged'):
        return redirect('home')
    user_type = request.session.get('user_type')
    if user_type != 'faculty':
        return redirect('home')

    faculty_id = request.session.get('username')
    courses = _get_courses_for_report(faculty_id)
    if request.method == 'POST':
        course_dep_year = request.POST.get('course_code').split('_')
        course_code = course_dep_year[0]
        department = course_dep_year[1]
        year = course_dep_year[2]
        
        lesson_plan = dict()
        lesson_plan['year'] = year
        lesson_plan['course'] = course_code
        lesson_plan['department'] = department
        lesson_plan['is_ready'] = True
        return render(request, 'faculty/filter_lesson_plan.html',{'course_filter':courses, 'report_data':lesson_plan})
    else:
        return render(request, 'faculty/filter_lesson_plan.html',{'course_filter':courses})


def generate_lesson_plan(request):    
    if request.method == 'POST':
        course_code = request.POST.get('report_course_code')
        course_title = Course.objects.get(course_code=course_code).title
        dep = request.POST.get('report_department').upper()
        department_code = _depcode(dep)
        dep_full_name = _dep_full_name(dep)
        batch = request.POST.get('report_course_year')
        hod_id = Hod_credential.objects.get(department=dep).hod_id
        hod_name = FacultyProfile.objects.get(faculty_id=hod_id).name
        faculty_name = FacultyProfile.objects.get(faculty_id=request.session.get('username')).name
        
        this_semester = (date.today().year - int(batch))*2
        if date.today().month >= 7:
            this_semester += 1
        
        lesson_data = _get_lesson_plan_for_course(course_code, batch, department_code)
        max_date = date.today().strftime('%d-%m-%Y')

        lesson_plan = dict()
        
        lesson_plan['semester'] = this_semester
        lesson_plan['date_upto'] = max_date
        lesson_plan['course_code'] = course_code
        lesson_plan['course_title'] = course_title
        lesson_plan['hod_name'] = hod_name
        lesson_plan['faculty_name'] = faculty_name
        lesson_plan['department_full_name'] = dep_full_name
        lesson_plan['total_classes'] = lesson_data.get('total', None)
        lesson_plan['dates'] = lesson_data.get('dates')
        
        return render(request, 'faculty/lesson_plan.html', {'report':lesson_plan})
    else:
        return render(request, 'faculty/lesson_plan.html', {})


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
    topic = post_array.get('topic','')
    topic = topic[:80]
    no_of_classes = int(post_array.get('no_of_classes',1))
    print('COURSE CODE',course_code, no_of_classes)
    for key, value in post_array.items():
        if key.startswith('reg_'):
            stu_inst = StudentProfile.objects.get(reg_no=key[4:])
            if stu_inst is not None:
                attend_instance = attendance.objects.create(reg_no=stu_inst, date=date, course_code=course_code, attendance=value, topic=topic, no_of_classes=no_of_classes, if_mod=False)
                attend_instance.save()


def _get_historical_course_filter(username=None, selected_batch=None, selected_semester=None, selected_course=None, selected_dep=None):
    if username is None:
        return dict()
    else:
        try:
            allotted_courses = list(Course_allot.objects.filter(faculty_id=username).values('year', 'course_code', 'semester').distinct())
            courses = list()
            years = list()
            semesters = list()
            depcodes = list()

            for course in allotted_courses:
                year = course.get('year')
                if year == selected_batch:
                    this_year = {'value':year, 'checked':True}
                else:
                    this_year = {'value':year, 'checked':False}
                if this_year not in years:
                    years.append(this_year)

                if selected_batch is not None:
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
                
                depcode_list = _get_depcodes()
                if selected_dep in [d['code'] for d in depcode_list]:
                    for dep in depcode_list:
                        if dep.get('code') == selected_dep:
                            dep['checked'] = True

            attendance_filters = {'courses':courses, 'years':years, 'semesters':semesters, 'depcodes':depcode_list}
            return attendance_filters

        except Course_allot.DoesNotExist:
            return dict()


def _get_attendance_data_for_course(course_code, batch, dep_code, inadequacy=False):
    try:
        students = list(attendance.objects.filter(course_code=course_code, reg_no__reg_no__startswith=(batch+dep_code)).values_list('reg_no', flat=True).distinct().order_by('reg_no'))
    except attendance.DoesNotExist:
        return dict()
    attendance_data = dict()
    student_attendance_list = []
    max_classes = 0
    students.sort()
    for reg_no in students:
        total = attendance.objects.filter(reg_no=reg_no, course_code=course_code).aggregate(total_classes=Sum('no_of_classes')).get('total_classes')
        total = total if total is not None else 0
        present = attendance.objects.filter(reg_no=reg_no, course_code=course_code, attendance='P').aggregate(classes_present=Sum('no_of_classes')).get('classes_present')
        present = present if present is not None else 0
        
        if total != 0:
            nocourse = False
            if total > max_classes:
                max_classes = total
        if inadequacy and present/total >= 0.75:
            continue
        student_attendance_list.append({'reg_no':reg_no, 'present':present})

    attendance_data['total'] = max_classes
    attendance_data['students'] = student_attendance_list

    return attendance_data


def _get_lesson_plan_for_course(course_code, batch, dep_code):
    try:
        classes = list(attendance.objects.filter(course_code=course_code, reg_no__reg_no__startswith=(batch+dep_code)).values('date','topic','no_of_classes').distinct().order_by('date'))
        total_classes = 0
        for lecture in classes:
            total_classes += lecture.get('no_of_classes')
    except attendance.DoesNotExist:
        return dict()

    attendance_data = dict()
    attendance_data['total'] = total_classes
    attendance_data['dates'] = classes
    return attendance_data


def _get_depcodes():
    depcode_list = list()
    depcode_list.append({'name':'Civil', 'code':'101', 'checked':False})
    depcode_list.append({'name':'Mechanical', 'code':'102', 'checked':False})
    depcode_list.append({'name':'EEE', 'code':'103', 'checked':False})
    depcode_list.append({'name':'ECE', 'code':'104', 'checked':False})
    depcode_list.append({'name':'CSE', 'code':'105', 'checked':False})
    depcode_list.append({'name':'EIE', 'code':'107', 'checked':False})

    return depcode_list


def _get_courses_for_report(faculty_id):
    odd_sem = False
    if date.today().month > 6:
        odd_sem = True

    faculty = FacultyProfile.objects.get(faculty_id=faculty_id)
    this_year = date.today().year
    allotted_courses = list()
    for i in range(4):
        allotted_courses += list(Course_allot.objects.annotate(odd=F('semester')%2).filter(year=str(this_year-i), faculty_id=faculty, odd=odd_sem).values('course_code','department','year'))

    codes = [d['course_code'] for d in allotted_courses]
    list_to_return = []
    for course in allotted_courses:
        course['duplicate'] = False
    
    new_list = list()
    for course in allotted_courses:
        if codes.count(course['course_code']) > 1:
            course['duplicate']=True
        new_list.append(course)
        
    return new_list


def _depcode(department):   
    depCode = None
    if department == 'EIE':
        depCode = '107'
    if department == 'CSE':
        depCode = '105'
    if department == 'ECE':
        depCode = '104'
    if department == 'EEE':
        depCode = '103'
    if department == 'ME':
        depCode = '102'
    if department == 'CE':
        depCode = '101'

    return depCode


def _dep_full_name(department):
    if department == 'EIE':
        return 'Electronics and Instrumentation Engineering'
    if department == 'CSE':
        return 'Computer Science and Engineering'
    if department == 'ECE':
        return 'Electronics and Communication Engineering'
    if department == 'EEE':
        return 'Electronics and Electrical Engineering'
    if department == 'ME':
        return 'Mechanical Engineering'
    if department == 'CE':
        return 'Civil Engineering'