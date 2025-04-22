from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    This serializer defines which fields are sent to the frontend when 
    a user authenticates or when user data is requested.
    """
    
    class Meta:
        model = User
        fields = [
            "id", 
            "email", 
            "first_name", 
            "last_name", 
            "role", 
            "is_active",
            "is_staff", 
            "is_superuser",
            # Add other fields from your User model that you want to expose
        ]
        read_only_fields = ["id", "is_active", "is_staff", "is_superuser"]

class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating User objects.
    
    This serializer may be used during registration if not using 
    the default allauth registration process.
    """
    
    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "first_name",
            "last_name",
            "role",
        ]
        extra_kwargs = {"password": {"write_only": True}}
    
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)