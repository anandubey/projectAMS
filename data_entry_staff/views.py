from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Credential

# Create your views here.

def index(request):
    if request.session.get('logged'):
        if request.session.get('hod_logged'):
            return redirect('hod_index')
        elif len(request.session.get('username')) == 10:
            return redirect('student')
        else:
            return redirect('faculty')
    
    if request.session.get('des_logged'):
        return redirect('des_dashboard')
    
    if request.method == 'GET':
        return HttpResponse("Data entry staff login page.")
    else:
        # Do something else


def dashboard(request):
    return HttpResponse("DES dashboard")

def create_batch(request):
    return HttpResponse("DES add batch")

# Add more and more