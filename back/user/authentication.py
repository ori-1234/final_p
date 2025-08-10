# user/authentication.py
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CookiesJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads the token from the access_token cookie.
    """
    def authenticate(self, request):
        """
        Override to check cookies instead of Authorization header
        """
        access_token = request.COOKIES.get('access_token')

        if not access_token:
            return None
        
        try:
            validated_token = self.get_validated_token(access_token)
            user = self.get_user(validated_token)
            return (user, validated_token)
        except AuthenticationFailed as e:
            logger.error(f"Authentication failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
