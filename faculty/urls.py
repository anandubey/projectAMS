from django.urls import path
from . import views

urlpatterns = [
    path('', views.faculty, name='faculty'),
    path('update_attendance/', views.update_attend, name='update_attend'),
    path('view_attendance/', views.view_attend, name='faculty_view_attend'),
    path('logout/', views.faculty_logout, name='faculty_logout'),
]
