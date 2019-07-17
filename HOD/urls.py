
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='hod_index' ),    
    path('dashboard/', views.dashboard, name='hod_dashboard' ),
    path('course_allotment/view/', views.view_courses, name='view_courses'),
    path('course_allotment/edit/<int:semester>', views.course_settings, name='course_settings' ),
    path('course_allotment/edit/', views.course_settings),
    path('course_allotment/save/', views.allot_courses, name='allot_courses'),
    path('logout/', views.hod_logout, name='hod_logout'),
    path('edit_attendance/', views.attendance_modifier, name='attendance_modifier'),
    path('view_attendance/semester/<int:sem>/reg/<str:reg_no>', views.view_student_attendance_semester_wise, name='hod_stu_att_view'),
    path('view_attendance/', views.attendance_viewer, name='attendance_viewer'),
]
