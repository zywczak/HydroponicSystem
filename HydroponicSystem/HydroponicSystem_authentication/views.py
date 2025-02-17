from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from .serializers import UserRegisterSerializer, UserLoginSerializer

class RegisterUserAPIView(APIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        """
        User registration.

        ### Request Body:
        - **email** (string, required): Must be a valid email format.
        - **password** (string, required): Must be at least 8 characters long.
        
        #### Example Request:
        POST /register/
        ```json
        {
            "email": "email@mail.com",
            "password":"kwakwa5!"
        }
        ```

        ### Responses:
        - **201 Created**: User created successfully.
        - **400 Bad Request**:  If the provided data is invalid.

        ### Example Response:
        ```json
        {
            "message": "User created successfully"
        }
        ```
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        """
        User login.

        ### Request Body:
        - **email** (string, required): Must be a valid email format.
        - **password** (string, required): Must be at least 8 characters long.
        
        #### Example Request:
        POST /register/
        ```json
        {
            "email": "email@mail.com",
            "password":"kwakwa5!"
        }
        ```

        ### Responses:
        - **200 OK**: 200 OK: If the login is successful, JWT token is returned.
        - **400 Bad Request**:  If the provided data is invalid.
        - **401 Unauthorized**: If the email or password is incorrect.
        
        ### Example Response:
        ```json
        {
            "token": "jwt-token"
        }
        ```
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)