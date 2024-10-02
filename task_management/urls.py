from django.contrib import admin
from django.urls import path, include  # Ensure 'include' is imported here
from . import views  # Import your views if needed

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('tasks.urls')),  # Ensure 'tasks.urls' is the correct module
    path('', views.home, name='home'),  # Optional: add a home path
]
