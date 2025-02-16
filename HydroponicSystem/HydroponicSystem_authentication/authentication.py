from datetime import datetime, timedelta
import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        jwt_token = request.META.get('HTTP_AUTHORIZATION')

        if jwt_token is None:
            return None
        
        jwt_token = JWTAuthentication.get_the_token_from_header(jwt_token)

        try:
            payload = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.exceptions.InvalidSignatureError:
            raise AuthenticationFailed('Invalid signature')
        except jwt.exceptions.DecodeError:
            return None
        except:
            return None

        id = payload.get('id')
        if id is None:
            return None

        user = User.objects.filter(id=id).first()
        if user is None:
            return None 

        return user, payload
    
    def authenticate_header(self, request):
        return 'Bearer'

    @classmethod
    def create_jwt(cls, user):
        payload = {
            'id': user.id,
            'email': user.email,
            'exp': int((datetime.now() + timedelta(hours=getattr(settings, 'JWT_CONFIG', {}).get('TOKEN_LIFETIME_HOURS', 8))).timestamp()),
            'iat': datetime.now().timestamp(),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    @classmethod
    def get_the_token_from_header(cls, token):
        return token.replace('Bearer', '').strip()
