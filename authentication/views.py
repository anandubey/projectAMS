from django.shortcuts import render, redirect
from .auth import login


def index(request):
    redirect_target = get_redirect_target(request)
    if redirect_target is not None:
        return redirect(redirect_target)
    else:
        if request.method == 'POST':
            return login(request)
        else:
            return render(request, 'authentication/index.html', {})


def pass_recovery(request):
    return render(request, 'authentication/recovery.html')


def get_redirect_target(request):
    if request.session.get('hod_logged'):
        return 'hod_dashboard'
    elif request.session.get('logged'):
        username = request.session.get('username')
        if len(username) == 10:
            return 'student'
        else:
            return 'faculty'
    else:
        return None