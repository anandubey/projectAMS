
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('recovery/', views.pass_recovery, name="recover"),
]
