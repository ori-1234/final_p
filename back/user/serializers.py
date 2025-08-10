from rest_framework import serializers
from .models import User, Note

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'password', 'last_name', 
                 'phone_number', 'is_verified', 'created_at', 'updated_at']
        read_only_fields = ('id', 'is_verified', 'created_at', 'updated_at')

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'desc']

