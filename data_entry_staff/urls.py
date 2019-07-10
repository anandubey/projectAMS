
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='des_index'),
    path('dashboard/', views.dashboard, name='des_dashboard'),
    path('create_batch/', views.index, name='des_create_batch'),
    
 
]
