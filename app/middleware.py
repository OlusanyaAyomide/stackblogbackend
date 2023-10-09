import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from rest_framework import status
from .constants import JWT_SECRET
from rest_framework.response import Response
from django.http import JsonResponse

class JWTMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get the JWT token from the request's Authorization header
        current_path = request.path
        path_components = current_path.split('/')
        request_path = path_components[-1]
        if(request_path == "login"):
            return self.get_response(request)
        
        authorization_header = request.headers.get('Authorization')
        if authorization_header is None:
            request.userId = None
            return self.get_response(request)
        if not authorization_header.startswith('Bearer '):
            request.userId = None
            return self.get_response(request)

        token = authorization_header.split(' ')[1]
        try:
            # Verify the JWT token using the secret key
            payload = jwt.decode(token,JWT_SECRET, algorithms=['HS256'])
            user_id = payload['id']
            User = get_user_model()
            request.userId = user_id  # Append the user to the request
        except jwt.ExpiredSignatureError:
            request.userId = None
            return self.get_response(request)
            # return JsonResponse({'detail': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except (jwt.InvalidTokenError, KeyError):
            request.userId = None
            return self.get_response(request)
            # return JsonResponse({'detail': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        except:
            request.userId = None
            return self.get_response(request)
        return self.get_response(request)
