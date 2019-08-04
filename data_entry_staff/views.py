from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import DES_Credential
from faculty.models import FacultyProfile
from student.models import StudentProfile
from authentication.models import FacultyCredential, StudentCredential
from HOD.models import Course, Semester_wise_electives
from datetime import date

# Create your views here.

def index(request):
    if request.session.get('logged'):
        if not des_logged(request):
            return redirect('home')
        else:
            return redirect('des_dashboard')

    if request.method == 'POST':
        return _des_login(request)
    else:
        return render(request, 'data_entry_staff/des_index.html')


def dashboard(request):
    if not des_logged(request):
        return redirect('home')

    return render(request, 'data_entry_staff/des_dashboard.html')


def create_batch(request):
    if not des_logged(request):
        return redirect('home')

    dep_list = _get_departments()
    dep_list.sort()

    if request.method == 'POST':
        if 'new_batch_option_btn' in request.POST:
            department = request.POST.get('new_batch_dep').upper()
            no_of_students = int(request.POST.get('new_batch_size'))
            starting_roll = request.POST.get('starting_roll_no')
            selected_year = request.POST.get('new_batch_year')
            first_roll_no = _get_roll_no(selected_year, department, starting_roll)
            if StudentProfile.objects.filter(reg_no__startswith=first_roll_no[:7]).exists():
                errormsg = 'The batch you asked has already been created. Ask database admin to make changes.'
                return render(request, 'data_entry_staff/des_create_batch.html', {'dep_list':dep_list, 'error':errormsg})
            page_data = {'department':department, 'no_of_students':range(no_of_students), 'first_roll_no':first_roll_no, 'dep_list':dep_list}
            return render(request, 'data_entry_staff/des_create_batch.html', page_data)

        elif 'new_batch_submit_btn' in request.POST:
            dep, year = _save_new_batch_in_db(_parse_new_batch(request.POST))
            success = 'New batch created for ' + dep + ' department in ' + str(year)
            return render(request, 'data_entry_staff/des_create_batch.html',{'dep_list':dep_list, 'success': success})
        else:
            return redirect('des_create_batch')
    else:
        return render(request, 'data_entry_staff/des_create_batch.html',{'dep_list': dep_list})

"""
def add_faculty(request):
    if not des_logged(request):
        return redirect('home')
    
    if request.method == 'POST':
        fac_id_entered = request.POST.get('faculty_id')
        if FacultyProfile.objects.filter(faculty_id=fac_id_entered).exists():
            errormsg = 'Faculty ID ' + str(fac_id_entered) + ' already exists.'
            return render(request, 'data_entry_staff/des_add_faculty.html', {'error':errormsg})
        
        fac_name_entered = request.POST.get('faculty_name')
        fac_email_entered = request.POST.get('faculty_email')
        fac_dep_entered = request.POST.get('faculty_dep')
        fac_password_entered = request.POST.get('faculty_password')

        new_faculty = FacultyProfile.objects.create(faculty_id=fac_id_entered, name=fac_name_entered, email=fac_email_entered, department=fac_dep_entered)
        new_faculty.save()
        new_faculty_credential = FacultyCredential.create(fac_id=new_faculty, password=faculty_password_entered)
        new_faculty_credential.save()

        return render(request, 'data_entry_staff/des_add_faculty.html', {'success':'Faculty added successfully.', 'new_faculty':new_faculty})
    else:
        return render(request, 'data_entry_staff/des_add_faculty.html', {})
"""

def add_course(request):
    if not des_logged(request):
        return redirect('home')
        
    if request.method == 'POST':

        course_code_entered = request.POST.get('course_code')
        course_title_entered = request.POST.get('course_title')
        course_is_elective = True if request.POST.get('is_elective') is not None else False
        
        print(course_code_entered, course_title_entered, course_is_elective)


        if Course.objects.filter(course_code=course_code_entered).exists():
            errormsg = 'Course code ' + course_code_entered + ' already exists in database.'
            return render(request, 'data_entry_staff/des_add_course.html',{'error':errormsg})

        new_course = Course.objects.create(course_code=course_code_entered.upper(), title=course_title_entered, elective=course_is_elective)
        new_course.save()

        return render(request, 'data_entry_staff/des_add_course.html',{'success':'Course added successfully.', 'new_course':new_course})
    else:
        return render(request, 'data_entry_staff/des_add_course.html',{})


def combine_course(request):
    if not des_logged(request):
        return redirect('home')

    dep_list = _get_departments()
    dep_list.sort()

    this_year = date.today().year
    year_list = list(range(this_year, this_year-4, -1))

    if request.method == 'POST':
        if 'combine_course_filter_btn' in request.POST:
            department_selected = request.POST.get('select_department')
            semester_selected = request.POST.get('select_semester')
            year_selected = request.POST.get('select_year')

            dep_prefix = department_selected[:2]
            electives_list = Course.objects.filter(elective=True, course_code__startswith=dep_prefix).values('course_code', 'title')
            print(electives_list)
            elective = {'courses':electives_list, 'elective_year':year_selected, 'elective_department':department_selected, 'elective_semester':semester_selected}
            return render(request, 'data_entry_staff/des_combine_course.html', {'dep_list':dep_list, 'year_list':year_list, 'elective': elective})

        elif 'combine_course_submit_btn' in request.POST:
            success = _save_electives(request.POST)
            return render(request, 'data_entry_staff/des_combine_course.html',{'dep_list':dep_list, 'year_list':year_list, 'success':success})
        else:
            return redirect('des_combine_courses')
    else:
        return render(request, 'data_entry_staff/des_combine_course.html',{'dep_list':dep_list, 'year_list':year_list})


def des_logout(request):
    request.session.clear()
    return redirect('des_index')


# Custom functions below


def _des_login(request):
    username_entered = request.POST.get('des_username')
    password_entered = request.POST.get('des_password')
    try:
        des_user = DES_Credential.objects.get(username=username_entered)
    except DES_Credential.DoesNotExist:
        return render(request,'data_entry_staff/des_index.html', {'error': "Wrong Username! Try Again"})

    if des_user.password == password_entered:
        request.session['username'] = username_entered
        request.session['logged'] = True
        request.session['user_type'] = 'data_entry_staff'
        request.session.set_expiry(0)
        return redirect('des_dashboard')
    else:
        return render(request,'data_entry_staff/des_index.html', {'error': "Wrong Password! Try Again"})


def des_logged(request):
    if not request.session.get('logged'):
        return False
    user_type = request.session.get('user_type')
    if user_type != 'data_entry_staff':
        return False
    else:
        return True


def _get_roll_no(year,department,first_roll):
    year = str(year)
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

    first_roll = str(first_roll)
    return year + depCode + first_roll


def _get_departments():
    return ['CSE', 'ECE', 'EIE', 'ME', 'EEE', 'CE']


def _parse_new_batch(post_array):
    new_batch_data = dict()
    new_batch_data['department'] = post_array.get('new_batch_department')
    first_roll = int(post_array.get('new_batch_first_roll'))
    new_batch_data['year'] = str(first_roll)[:4]
    no_of_students = int(post_array.get('no_of_students'))

    batch_list = []
    single_student_data = dict()
    for i in range(no_of_students):
        current_roll = str(first_roll + i)
        single_student_data['reg_no'] = post_array.get('nb_reg_' + current_roll)
        single_student_data['name'] = post_array.get('nb_name_' + current_roll)
        single_student_data['email'] = post_array.get('nb_email_' + current_roll)
        batch_list.append(single_student_data.copy())
    
    new_batch_data['students'] = batch_list
    return new_batch_data


def _save_new_batch_in_db(new_batch_data):
    department = new_batch_data.get('department')
    year = new_batch_data.get('year')
    for student in new_batch_data['students']:
        password = _make_password(student)
        new_student_in_db = StudentProfile.objects.create(reg_no=student['reg_no'], name=student['name'], email=student['email'], department=department)
        new_student_in_db.save()
        new_student_cred_in_db = StudentCredential.objects.create(reg_no=new_student_in_db, password=password)
        new_student_cred_in_db.save()

    return department, year


def _make_password(new_student):
    initials = ''.join(new_student['name'].split())[:3].lower()
    year = new_student['reg_no'][2:4]
    roll_no = new_student['reg_no'][6:]

    return year + initials + roll_no


#def _save_electives(elective_data):
    


def _save_electives(post_array):
    year = str(post_array.get('elective_year'))
    department = post_array.get('elective_department')
    semester = int(post_array.get('elective_semester'))

    elective_courses = []
    for var in post_array:
        if var.startswith('elective_choice_'):
            if post_array.get(var) == 'on':
                elective_courses.append(var.split('_')[-1])
    
    elective_courses.sort()
    courses_db_string = '-'.join(elective_courses)

    if Semester_wise_electives.objects.filter(department=department, year=year, semester=semester).exists():
        new_elective_list = Semester_wise_electives.objects.get(department=department, year=year, semester=semester)
        new_elective_list.elective_courses = courses_db_string
        new_elective_list.save()
    else:
        new_elective_list = Semester_wise_electives.objects.create(department=department, year=year, semester=semester, elective_courses=courses_db_string)
        new_elective_list.save()
    return 'Electives saved for year ' + year + ' in ' + department + ' department semester ' + str(semester)