from django.urls import path, include
from rest_framework import routers
from tasks import views
from .views import TaskViewSet
from .views import TaskAssignView 
from .views import UserViewSet, TaskViewSet, TaskAssignView, assign_self_task
from django.urls import path
from .views import dashboard
from .views import TaskList



app_name = 'tasks'

# Create a router and register our viewsets with it.
router = routers.DefaultRouter()
router.register('tasks', views.TaskViewSet, basename='task')  # Use TaskViewSet for handling tasks

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),  # Includes the router URLs for tasks
    path('me/all/', views.my_tasks, name='my-tasks'),
    path('me/<int:pk>/', views.task_detail, name='task-detail'),
    path('me/completed/', views.tasks_completed, name='completed'),
    path('me/incompleted/', views.tasks_incompleted, name='incompleted'),
    path('export/csv/', views.save_as_csv, name='save-as-csv'),
    path('export/xls/', views.save_as_xls, name='save-as-xls'),
    
    #  endpoints
    path('register/', views.register, name='register'),  
     path('login/', views.login, name='login'), 
     path('assign-task/', TaskAssignView.as_view(), name='assign_task'),
     path('api/assign-self-task/', assign_self_task, name='assign_self_task'),
     path('dashboard/', dashboard, name='dashboard'),  
     path('api/tasks/', TaskList.as_view(), name='task-list'),
   
]
