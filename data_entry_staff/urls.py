
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='des_index'),
    path('dashboard/', views.dashboard, name='des_dashboard'),
    path('create_batch/', views.create_batch, name='des_create_batch'),
    #path('add_faculty/', views.add_faculty, name='des_add_faculty'),
    path('add_course/', views.add_course, name='des_add_course'),
    path('combine_courses/', views.combine_course, name='des_combine_courses'),
    path('logout/', views.des_logout, name='des_logout'),
]
