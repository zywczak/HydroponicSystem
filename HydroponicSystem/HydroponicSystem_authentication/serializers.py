from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import AuthenticationFailed
from .authentication import JWTAuthentication

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100, min_length=8)

    class Meta:
        model = get_user_model()
        fields = ['email', 'password']

    def create(self, validated_data):
        password = validated_data.get('password', None)
        email = validated_data.get('email')
        user = self.Meta.model(
            email=email,
        )

        user.set_password(password)
        user.save()
        return user
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(max_length=100, min_length=8)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        user = authenticate(username=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials.")

        token = JWTAuthentication.create_jwt(user)

        return {"token": token}
