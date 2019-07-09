
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path('student/', include('student.urls')),
    path('faculty/',include('faculty.urls')),
    path('hod/', include('HOD.urls')),,
    path('des/',include('data_entry_staff.urls')),
]
