from django.urls import path
from . import views

urlpatterns = [
    path('', views.faculty, name='faculty'),
    path('update_attendance/', views.update_attend, name='update_attend'),
    path('view_attendance/', views.view_attend, name='faculty_view_attend'),
    path('attendance_report/', views.attendance_report, name='attendance_report'),
    path('attendance_report/print', views.generate_report, name='print_report'),
    path('lesson_plan', views.lesson_plan, name='lesson_plan'),
    path('lesson_plan/print',views.generate_lesson_plan, name='print_lesson_plan'),
    path('logout/', views.faculty_logout, name='faculty_logout'),
]
