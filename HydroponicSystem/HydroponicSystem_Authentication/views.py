from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from .serializers import UserRegisterSerializer
from django.contrib.auth import authenticate
from .authentication import JWTAuthentication

class RegisterUserAPIView(APIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_user = serializer.save()
            if new_user:
                return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginAPIView(APIView):
	permission_classes = [AllowAny]

	def post(self, request):
		email = request.data.get('email', None)
		user_password = request.data.get('password', None)
  
		if not user_password:
			return Response({"error": "User password is required."}, status=status.HTTP_400_BAD_REQUEST)

		if not email:
			return Response({"error": "User email is required."}, status=status.HTTP_400_BAD_REQUEST)

		user_instance = authenticate(username=email, password=user_password)
		if not user_instance:
			return Response({"error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)

		access_token = JWTAuthentication.create_jwt(user_instance)
		return Response({'token': access_token}, status=status.HTTP_200_OK)