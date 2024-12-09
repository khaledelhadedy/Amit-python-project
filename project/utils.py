from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings

def create_response(message, data=None, errors=None, status_code=status.HTTP_200_OK):
    
    if errors is None:
        response_data = {
            'message': message,
            'data': data,
        }
        
    else:
        response_data = {
            'message': message,
            'errors': errors
        }
    return Response(response_data, status=status_code)



def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    if settings.SIMPLE_JWT.get('ROTATE_REFRESH_TOKENS', False):
        refresh.set_jti()
        refresh.set_exp()

    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
    }