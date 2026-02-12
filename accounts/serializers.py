from django.core import exceptions
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email','password')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value
        
    def validate_password(self, value):
        validate_password(value)
        return value
        
    def create(self , validated_data):
        return User.objects.create_user(**validated_data)
        
class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email','is_verified','is_staff','created_date')

