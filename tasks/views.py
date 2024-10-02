from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, TaskSerializer
import csv
from django.http import JsonResponse, HttpResponse
from rest_framework import viewsets, generics, permissions
from .models import Task
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework import serializers


class TaskList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TaskList(APIView):
    def get(self, request):
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TaskListView(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.CharField(source='assigned_to.username', read_only=True)  # Returns username

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'status', 'assigned_to', 'created_at', 'updated_at']



class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


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
        return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid credentials or user is not an admin.'}, status=status.HTTP_403_FORBIDDEN)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can access this view


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can access this view


def my_tasks(request):
    tasks = Task.objects.filter(user=request.user)
    return render(request, 'tasks/my_tasks.html', {'tasks': tasks})


def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'tasks/task_detail.html', {'task': task})


@api_view(['POST'])
def complete_task(request, task_id):
    try:
        task = Task.objects.get(id=task_id)
        task.status = 'completed'  # Update status as needed
        task.save()
        return Response({'message': 'Task marked as completed.'}, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def tasks_completed(request):
    completed_tasks = Task.objects.filter(status='completed')
    return Response({'completed_tasks': TaskSerializer(completed_tasks, many=True).data})


@api_view(['POST'])
def tasks_incompleted(request):
    incompleted_tasks = Task.objects.filter(status='incomplete')
    return Response({'incompleted_tasks': TaskSerializer(incompleted_tasks, many=True).data})


@api_view(['POST'])
def save_as_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tasks.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Task Name', 'Status'])

    tasks = Task.objects.all()
    for task in tasks:
        writer.writerow([task.id, task.name, task.status])

    return response


@api_view(['POST'])
def save_as_xls(request):
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="tasks.xls"'
    # Example data; replace with your actual data handling logic
    df = pd.DataFrame({'Task': ['Task1', 'Task2'], 'Status': ['Complete', 'Pending']})
    df.to_excel(response, index=False)
    return response


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
        return JsonResponse({'message': 'Login successful!'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid username or password'}, status=400)


class TaskAssignView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        if self.request.user.userprofile.is_admin:
            serializer.save(user=self.request.data.get('assigned_to'))
        else:
            raise permissions.PermissionDenied("You do not have permission to assign tasks.")

    def post(self, request, *args, **kwargs):
        if request.user.userprofile.is_admin:
            return super().post(request, *args, **kwargs)
        else:
            return Response({'error': 'You do not have permission to assign tasks.'}, status=status.HTTP_403_FORBIDDEN)

@api_view(['POST'])
def assign_self_task(request):
    """
    Allows a user to assign a task to themselves.
    """
    task_id = request.data.get('task_id')  # assuming the task ID is passed in the request
    try:
        task = Task.objects.get(id=task_id)
        task.user = request.user  # assign the task to the logged-in user
        task.save()
        return Response({'message': 'Task assigned to self successfully!'}, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)

def dashboard(request):
    tasks = []  # Default to an empty list

    if request.user.is_authenticated:
        # Fetch tasks assigned to the current user
        tasks = Task.objects.filter(assigned_to=request.user)
        
    return render(request, 'your_template.html', {'tasks': tasks})