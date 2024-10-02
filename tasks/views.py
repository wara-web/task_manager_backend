from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from .serializers import TaskSerializer
import csv
from django.http import JsonResponse

from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer
from rest_framework import generics,permissions

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


@api_view(['POST'])
def register(request):
    """
    Handle user registration
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'id': user.id, 
            'username': user.username,
            'message': 'User registered successfully.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # You can return any response you need, including user info if necessary
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=400)
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@api_view(['POST'])
def admin_login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None and user.userprofile.is_admin:
        # Login successful for admin user
        return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
    else:
        # Login failed
        return Response({'error': 'Invalid credentials or user is not an admin.'}, status=status.HTTP_403_FORBIDDEN)
    
def my_tasks(request):
    # Logic to get the user's tasks
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/my_tasks.html', {'tasks': tasks})

def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})

def tasks_completed(request):
    # Your logic to get completed tasks
    completed_tasks = Task.objects.filter(status='completed')  # Assuming you have a Task model with a 'status' field
    return render(request, 'tasks/completed_tasks.html', {'completed_tasks': completed_tasks})

def tasks_incompleted(request):
    # Your logic to get incomplete tasks
    incompleted_tasks = Task.objects.filter(status='incomplete')  # Assuming you have a Task model with a 'status' field
    return render(request, 'tasks/incompleted_tasks.html', {'incompleted_tasks': incompleted_tasks})

def save_as_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tasks.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Task Name', 'Status'])  # Add your headers here

    # Assuming you have a Task model
    tasks = Task.objects.all()  # Fetch all tasks
    for task in tasks:
        writer.writerow([task.id, task.name, task.status])  # Adjust based on your Task model fields

    return response

def save_as_xls(request):
    # Your logic to save data as XLS
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="tasks.xls"'
    # Example data (replace with your actual data)
    df = pd.DataFrame({'Task': ['Task1', 'Task2'], 'Status': ['Complete', 'Pending']})
    df.to_excel(response, index=False)
    return response

@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Authenticate the user
    user = authenticate(username=username, password=password)
    if user is not None:
        # User is authenticated, return a success response
        return JsonResponse({'message': 'Login successful!'}, status=200)
    else:
        # Invalid credentials
        return JsonResponse({'error': 'Invalid username or password'}, status=400)

class TaskAssignView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # Ensure the user is an admin before assigning tasks
        if self.request.user.userprofile.is_admin:
            serializer.save(user=self.request.data.get('assigned_to'))  # Get assigned user from request data
        else:
            raise permissions.PermissionDenied("You do not have permission to assign tasks.")

    def post(self, request, *args, **kwargs):
        if request.user.userprofile.is_admin:
            return super().post(request, *args, **kwargs)
        else:
            return Response({'error': 'You do not have permission to assign tasks.'}, status=status.HTTP_403_FORBIDDEN)