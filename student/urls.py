
from django.urls import path
from . import views
urlpatterns = [
    path('', views.student, name='student'),
    path('logout/', views.student_logout, name='student_logout'),
]
