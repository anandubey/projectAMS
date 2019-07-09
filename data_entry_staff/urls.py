
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='des_index'),
    path('dashboard/', views.dashboard, name='des_dashboard'),
    path('create_batch/', views.index, name='des_create_batch'),
    path('add_student/', views.index, name='des_add_student'),
    path('add_faculty/', views.index, name='des_add_faculty'),
    path('add_course/', views.index, name='des_add_course'),
    path('combine_courses/', views.index, name='des_combine_courses'),

    path('logout/', views.logout, name='des_logout'),
]
