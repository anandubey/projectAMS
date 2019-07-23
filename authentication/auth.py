from django.shortcuts import render, redirect
from .models import StudentCredential, FacultyCredential


def login(request):
    username_entered = request.POST.get('username')
    password_entered = request.POST.get('password')

    user_type = None
    if len(username_entered) == 10:
        try:
            user_instance = StudentCredential.objects.get(reg_no=username_entered)
            user_type = 'student'
        except StudentCredential.DoesNotExist:
            return render(request, 'authentication/index.html', {'error': "Invalid Username! Try Again"})
    else:
        try:
            user_instance = FacultyCredential.objects.get(fac_id=username_entered)
            user_type = 'faculty'
        except FacultyCredential.DoesNotExist:
            return render(request, 'authentication/index.html', {'error': "Invalid Username! Try Again"})
    
    if user_instance.password == password_entered:
        request.session['username'] = username_entered
        request.session['logged'] = True
        request.session['user_type'] = user_type
        request.session.set_expiry(0)
        return redirect('home')
    else:
        return render(request, 'authentication/index.html', {'error': "Wrong Password! Try Again."})
