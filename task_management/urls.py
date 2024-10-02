from django.contrib import admin
from django.urls import path, include  
from . import views  # Import your views if needed

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('tasks.urls')), 
    path('', views.home, name='home'),  
   ]
