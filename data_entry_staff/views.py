from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import DES_Credential
from faculty.models import FacultyProfile
from student.models import StudentProfile

# Create your views here.

def index(request):
    if not _logged(request):
        return redirect('home')

    if request.method == 'POST':
        return _des_login(request)
    else:
        return HttpResponse("Data entry staff login page.")


def dashboard(request):
    if not _logged(request):
        return redirect('home')

    return HttpResponse("DES dashboard")


def create_batch(request):
    if not _logged(request):
        return redirect('home')

    if request.method == 'POST':
        pass
    else:
        return HttpResponse("DES add batch")


def add_faculty(request):
    if not _logged(request):
        return redirect('home')
    
    if request.method == 'POST':
        faculty_id = request.POST.get('faculty_id_entered')
        if FacultyProfile.objects.filter(faculty_id=faculty_id).exists():
            return render(request, 'data_entry_staff/des_add_faculty.html', {'error: Faculty with given ID exists!'})
        
        faculty_name = request.POST.get('faculty_name_entered')
        faculty_email = request.POST.get('faculty_email_entered')
        faculty_department = request.POST.get('faculty_dep_entered')

    else:
        return HttpResponse('DES Add faculty page')


def add_course(request):
    if not _logged(request):
        return redirect('home')
        
    return HttpResponse('DES add course page')


def combine_course(request):
    if not _logged(request):
        return redirect('home')
        
    return HttpResponse('DES course combine page.')


def des_logout(request):
    request.session.clear()
    return redirect('des_index')

# Add more and more


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


def _logged(request):
    if not request.session.get('logged'):
        return False
    user_type = request.session.get('user_type')
    if user_type != 'data_entry_staff':
        return False
    else:
        return True