from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Min, Max, Sum
from .models import Hod_credential, Course, Semester_wise_course, Course_allot, Semester_wise_electives
from faculty.models import FacultyProfile, attendance
from student.models import StudentProfile
from datetime import date


def index(request):
    if request.method == "POST":
        username_entered = request.POST.get('username')
        password_entered = request.POST.get('password')
        if authenticate(username_entered, password_entered):
            hod_login(request)
            return redirect('hod_dashboard')
        else:
            return render(request, 'HOD/hod_index.html',{'invalid_cred':'Invalid credentials!'})
    else:
        if not request.session.get('logged'):
            return render(request, 'HOD/hod_index.html',{})
        user_type = request.session.get('user_type')
        if user_type != 'HOD':
            return redirect('home')
        else:
            return redirect('hod_dashboard')


def dashboard(request):
    if _hod_is_logged(request):
        semesters = _get_semesters(request)
        return render(request,'HOD/hod_home.html',{'sem':semesters})
    else:
        return redirect('home')


def course_settings(request,semester=None):
    if not _hod_is_logged(request):
        return redirect('home')
    
    if request.method == 'GET':
        if semester is None:
            return redirect('hod_dashboard')
        else:
            batch = date.today().year - semester//2
            semesters = _get_semesters(request)
            active_username = request.session.get('username')
            hod_instance = Hod_credential.objects.get(hod_id=active_username)
            department = hod_instance.department
            faculty_group = FacultyProfile.objects.all()
            faculties = []
            courses = []
            try:
                course_codes = Semester_wise_course.objects.get(semester=semester, department=department).courses.split('-')
                if semester > 4:
                    try:
                        course_codes += Semester_wise_electives.objects.get(department=department, semester=semester, year=date.today().year).elective_courses.split('-')
                    except Semester_wise_electives.DoesNotExist:
                        pass
                for faculty in faculty_group:
                    faculties.append({'id':faculty.faculty_id, 'name':faculty.name})
                for code in course_codes:
                    try:
                        course = Course.objects.get(course_code=code)
                        courses.append({'code': course.course_code, 'title':course.title})
                    except Course.DoesNotExist:
                        pass
            except Semester_wise_course.DoesNotExist:
                pass
            data = {'courses': courses, 'faculties':faculties,'sem':semesters, 'batch':batch, 'semester':semester}
            return render(request, 'HOD/course_setting.html', data)
    else:
        return redirect('course_settings', semester=semester)


def view_courses(request):
    if not _hod_is_logged(request):
        return redirect('home')
    
    semesters = _get_semesters(request)
    username = request.session.get('username')
    department = Hod_credential.objects.get(hod_id=username).department
    if request.method == 'POST':
        selected_batch = request.POST.get('select_batch')
        batch_filter = _get_batches_filter(selected=selected_batch)
        selected_semester = request.POST.get('select_semester')
        semester_filter = _get_semesters_filter(request, selected=selected_semester)
        course_allotment = Course_allot.objects.filter(year=selected_batch, department=department, semester=int(selected_semester))
        course_mapping = _get_course_map(course_allotment)
        if len(course_mapping) == 0:
            no_course = True
        else:
            no_course = False
        template_data = {'sem': semesters, 'courses':course_mapping, 'batch_filter':batch_filter, 'semester_filter':semester_filter, 'no_course':no_course}
        return render(request, 'HOD/course_view.html', template_data)
    else:
        batch_filter = _get_batches_filter(selected=None)
        semester_filter = _get_semesters_filter(request, selected=None)
        template_data = {'sem': semesters, 'batch_filter':batch_filter, 'semester_filter':semester_filter}
        return render(request, 'HOD/course_view.html', template_data)


def attendance_modifier(request):
    if not _hod_is_logged(request):
        return redirect('home')
    
    semesters = _get_semesters(request)
    if request.method == 'POST':
        if 'att_data_submit_btn' in request.POST:
            reg_no_to_modify = request.POST.get('hod_attend_edit_reg_no')
            start_date_entered = request.POST.get('hod_attend_edit_start_date')
            end_date_entered = request.POST.get('hod_attend_edit_end_date')
            print(reg_no_to_modify, start_date_entered, end_date_entered)
            if _modify_attendance_for_student(reg_no_to_modify, start_date_entered, end_date_entered):
                status = 'Attendance modified successfully'
            else:
                status = 'Failed to modify attendance'
            attendance_data = dict()
            try:
                student = StudentProfile.objects.get(reg_no=reg_no_to_modify)
                attendance_data = _get_attendance_data_for_student(student)
                return render(request, 'HOD/hod_attend_edit.html', {'sem': semesters, 'attendance':attendance_data, 'status':status})
            except StudentProfile.DoesNotExist:
                #messages.error(request, 'Failed to modify attendance')
                return redirect('attendance_modifier')

        elif 'att_mod_filter_btn' in request.POST:
            reg_no_entered = request.POST.get('hod_attend_edit_regno')
            attendance_data = dict()
            if len(reg_no_entered) != 10 or (not reg_no_entered.isdigit()):
                return render(request, 'HOD/hod_attend_edit.html', {'sem': semesters, 'invalid_reg':True})
            try:
                student = StudentProfile.objects.get(reg_no=reg_no_entered)
                attendance_data = _get_attendance_data_for_student(student)
                return render(request, 'HOD/hod_attend_edit.html', {'sem': semesters, 'attendance':attendance_data})
            except StudentProfile.DoesNotExist:
                return render(request, 'HOD/hod_attend_edit.html', {'sem': semesters, 'not_found':True})
        else:
            return redirect('attendance_modifier')
    else:
        return render(request, 'HOD/hod_attend_edit.html', {'sem': semesters})


def view_student_attendance_semester_wise(request, sem=None, reg_no=None):
    notLoggedAccessPageContent = """
        You must login as HOD to see this page.
        <br>
        <input type="button" onclick="window.close()" value="Close this window">
    """

    if not _hod_is_logged(request):
        return HttpResponse(notLoggedAccessPageContent)

    template_data = dict()
    if sem is None or reg_no is None:
        return redirect('attendance_viewer')
    else:
        try:
            student = StudentProfile.objects.get(reg_no=reg_no)
        except StudentProfile.DoesNotExist:
            template_data['invalid_reg'] = True
            return render(request, 'HOD/hod_attend_view_student.html', template_data)

        logged_username = request.session.get('username')
        try:
            hod = Hod_credential.objects.get(hod_id=logged_username)
            if student.department != hod.department:
                template_data['invalid_reg'] = True
            else:
                course_year = str(int(reg_no[:4])+ (sem//2))
                courses = Semester_wise_course.objects.get(department=student.department, semester=sem).courses.split('-')
                if sem > 4:
                    try:
                        courses += Semester_wise_electives.objects.get(department=student.department, semester=sem, year=course_year).elective_courses.split('-')
                    except Semester_wise_electives.DoesNotExist:
                        pass
                    
                att_data_list = []                                         # using list of dictionaries to store attendance 
                for course_code in courses:
                    total = attendance.objects.filter(reg_no=student, course_code=course_code).aggregate(total_classes=Sum('no_of_classes')).get('total_classes')
                    total = total if total is not None else 0
                    present = attendance.objects.filter(reg_no=student, course_code=course_code, attendance='P').aggregate(classes_present=Sum('no_of_classes')).get('classes_present')
                    present = present if present is not None else 0

                    if total != 0:
                        percent_present = (present/total)*100
                    else:
                        percent_present = 0.0
                    less_attendance = False
                    if percent_present < 75:
                        less_attendance = True
                    att_data = {'course_code':course_code, 'total_classes':total, 'attended':present, 'percent':percent_present, 'less_attend':less_attendance}
                    att_data_list.append(att_data)
                template_data['user_instance'] = student
                template_data['att_data_list'] = att_data_list
                template_data['stu_sem'] = sem
            return render(request, 'HOD/hod_attend_view_student.html', template_data)

        except Hod_credential.DoesNotExist:
            return redirect('attendance_viewer')


def attendance_viewer(request):
    semesters = _get_semesters(request)
    department = Hod_credential.objects.get(hod_id=request.session.get('username')).department
    if request.method == 'POST':
        selected_batch = request.POST.get('select_batch')
        selected_semester = request.POST.get('select_semester')
        if selected_batch == '' or selected_semester == '':
            return redirect('attendance_viewer')
        
        this_semester = (date.today().year - int(selected_batch))*2
        if date.today().month >= 7:
            this_semester += 1

        batch_filter = _get_batches_filter(selected=selected_batch)
        semester_filter = _get_semesters_filter(request, selected=selected_semester)
        attendance_data = _get_attendance_data_for_batch(department, batch=selected_batch, semester=selected_semester)
        
        template_data = {'sem': semesters, 'batch_filter':batch_filter, 'semester_filter':semester_filter, 'attendance':attendance_data, 'selected_semester':selected_semester}
        return render(request, 'HOD/hod_attend_view.html', template_data)
    else:
        batch_filter = _get_batches_filter(selected=None)
        semester_filter = _get_semesters_filter(request, selected=None)
        template_data = {'sem': semesters, 'batch_filter':batch_filter, 'semester_filter':semester_filter, 'freshpage':True}
        return render(request, 'HOD/hod_attend_view.html', template_data)


def allot_courses(request):
    if request.method == 'POST':
        print("Received allotment")
        batch = request.POST.get('allotment_batch')
        course_semester = int(request.POST.get('allotment_semester'))
        course_department = Hod_credential.objects.get(hod_id=request.session.get('username')).department
        course_map = _parse_course_mapping(request)
        print(course_map)
        for course_code, faculty_id in course_map.items():
            course_instance = Course.objects.get(course_code=course_code.upper())
            faculty_instance = FacultyProfile.objects.get(faculty_id=faculty_id.upper())
            try:
                allotment_object = Course_allot.objects.get(year=batch, department=course_department, course_code=course_instance,semester=course_semester)
                allotment_object.faculty_id = faculty_instance
                allotment_object.save()
            except Course_allot.DoesNotExist:
                allotment_object = Course_allot.objects.create(year=batch, department=course_department, course_code=course_instance, faculty_id=faculty_instance, semester=course_semester)
                allotment_object.save()
        messages.success(request, "Course allotment has been saved.")
        return redirect('course_settings', semester=course_semester)
    else:
        return redirect('hod_dashboard')


def _get_semesters(request):
    current_hod = request.session.get('username')
    department = Hod_credential.objects.get(hod_id=current_hod).department
    if department == 'SH':
        return [1,2]
    else:
        return [3,4,5,6,7,8]


def _get_course_map(allotment_filter):
    course_map_list = list()
    if allotment_filter is None:
        return course_map_list
    else:
        for allotment_obj in allotment_filter:
            course_obj = allotment_obj.course_code
            course_code = course_obj.course_code
            course_title = course_obj.title
            faculty_name = allotment_obj.faculty_id.name
            course_map_list.append({'code':course_code, 'title':course_title, 'faculty':faculty_name})
        return course_map_list


def _get_semesters_filter(request, selected=None):
    current_hod = request.session.get('username')
    department = Hod_credential.objects.get(hod_id=current_hod).department
    semesters = dict()
    if selected is None:
        selected = '_____'
    if department == 'SH':
        for semester in range(1,3):
            if selected == str(semester):
                semesters[semester] = True
            else:
                semesters[semester] = False
    else:
        for semester in range(3,9):
            if selected == str(semester):
                semesters[semester] = True
            else:
                semesters[semester] = False
    return semesters


def _get_batches_filter(selected=None):
    batches_list = list(Course_allot.objects.values_list('year', flat=True).distinct())
    batches = dict()
    for batch in batches_list:
        if selected != batch:
            batches[batch] = False
        else:
            batches[batch] = True
    return batches

# Below function seems to be useless
def _get_course_filter(request, selected=None, semester=None):
    current_hod = request.session.get('username')
    department = Hod_credential.objects.get(hod_id=current_hod).department
    if semester is None:
        return []
    try:
        course_codes = str(Semester_wise_course.objects.get(department=department, semester=semester).courses).split('-')
    except Semester_wise_course.DoesNotExist:
        return []

    course_filter = []
    for course_code in course_codes:
        course_title = Course.objects.get(course_code=course_code).title
        if course_code != selected:
            course_filter.append({'code':course_code, 'title':course_title, 'checked':False})
        else:
            course_filter.append({'code':course_code, 'title':course_title, 'checked':True})
    
    return course_filter
    

def _get_attendance_data_for_batch(department, batch=None, semester=None):
    if semester is None or batch is None:
        return dict()
    else:
        semester = int(semester)
        try:
            course_year = str(int(batch) + semester // 2)
            courses = Semester_wise_course.objects.get(department=department, semester=semester).courses.split('-')
            if int(semester) > 4:
                try:
                    courses += Semester_wise_electives.objects.get(department=department, semester=semester, year=course_year).elective_courses.split('-')
                except Semester_wise_electives.DoesNotExist:
                    pass
            students = list(StudentProfile.objects.filter(reg_no__startswith=batch).values_list('reg_no', flat=True).order_by('reg_no'))
        except Semester_wise_course.DoesNotExist:
            return dict()
        except StudentProfile.DoesNotExist:
            return dict()
    attendance_data = dict()
    student_attendance_list = []
    
    for reg_no in students:
        percent_list = []
        nocourse = True
        for course_code in courses:
            total = attendance.objects.filter(reg_no=reg_no, course_code=course_code).aggregate(total_classes=Sum('no_of_classes')).get('total_classes')
            total = total if total is not None else 0
            present = attendance.objects.filter(reg_no=reg_no, course_code=course_code, attendance='P').aggregate(classes_present=Sum('no_of_classes')).get('classes_present')
            present = present if present is not None else 0
            if total != 0:
                nocourse = False
                percent_present = (present/total)*100
                percent_list.append(percent_present)
            else:
                percent_list.append(0.0)
        if nocourse:
            return dict()
        student_attendance_list.append({'reg_no':reg_no, 'percent':percent_list})
    attendance_data['courses'] = courses
    attendance_data['students'] = student_attendance_list

    return attendance_data


def _get_attendance_data_for_student(student_profile):
    data = dict()
    this_semester = (date.today().year - int(student_profile.reg_no[:4]))*2
    if date.today().month >= 7:
        this_semester += 1
    
    data['reg_no'] = student_profile.reg_no
    data['stu_name'] = student_profile.name

    if this_semester % 2 == 0:
        data['min_date'] = date(date.today().year, 1, 1).strftime('%Y-%m-%d')
        data['max_date'] = date(date.today().year, 6, 30).strftime('%Y-%m-%d')
    else:
        data['min_date'] = date(date.today().year, 7, 1).strftime('%Y-%m-%d')
        data['max_date'] = date(date.today().year, 12, 31).strftime('%Y-%m-%d')
    
    att_data_list = list()
    course_year = str(date.today().year)
    courses = Semester_wise_course.objects.get(department=student_profile.department, semester=this_semester).courses.split('-')
    if this_semester > 4:
        try:
            courses += Semester_wise_electives.objects.get(department=student_profile.department, semester=this_semester, year=course_year).elective_courses.split('-')
        except Semester_wise_electives.DoesNotExist:
            pass
    
    for course_code in courses:
        total = attendance.objects.filter(reg_no=student_profile, course_code=course_code).aggregate(total_classes=Sum('no_of_classes')).get('total_classes')
        total = total if total is not None else 0
        present = attendance.objects.filter(reg_no=student_profile, course_code=course_code, attendance='P').aggregate(classes_present=Sum('no_of_classes')).get('classes_present')
        present = present if present is not None else 0
        if total != 0:
            percent_present = (present/total)*100
        else:
            percent_present = 0.0            
        att_data_list.append(percent_present)
    
    data['courses'] = courses
    data['percentages'] = att_data_list
    return data


def _modify_attendance_for_student(reg_no, start_date, end_date):
    attendance_filter = attendance.objects.filter(reg_no=reg_no, date__range=[start_date, end_date])
    if attendance_filter is None:
        return False
    for attendance_ins in attendance_filter:
        attendance_ins.attendance = 'P'
        attendance_ins.if_mod = True
        attendance_ins.save()
    return True


def _parse_course_mapping(request):
    course_map = dict()
    for key, value in request.POST.items():
        if key.startswith('course_'):
            course_map[key[7:]] = value
    return course_map

# AUTHENTICATION FUNCTIONS WRITTEN BELOW

def hod_login(request):
    request.session['username'] = request.POST.get('username')
    request.session['logged'] = True
    request.session['user_type'] = 'HOD'


def authenticate(username=None, password=None):
    if username is None or password is None:
        return False
    try:
        hod_ins = Hod_credential.objects.get(hod_id=username)
    except Hod_credential.DoesNotExist:
        return False
    if hod_ins is not None:
        if password == hod_ins.password:
            return True
        else:
            return False
    else:
        return False


def _hod_is_logged(request):
    if request.session.get('logged'):
        user_type = request.session.get('user_type')
        if user_type != 'HOD':
            return False
        else:
            return True
    else:
        return False


def hod_logout(request):
    request.session.clear()
    return redirect('hod_index')