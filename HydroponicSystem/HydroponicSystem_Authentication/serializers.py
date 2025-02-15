from rest_framework import serializers
from django.contrib.auth import get_user_model

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