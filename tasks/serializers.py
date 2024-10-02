# serializers.py

from django.contrib.auth.models import User
from rest_framework import serializers

from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']  # You can add more fields if needed

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            # You should also hash the password before saving
        )
        user.set_password(validated_data['password'])  # Hashing the password
        user.save()
        return user
