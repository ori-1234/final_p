from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from .models import LoginHistory, User, Note
from .serializers import UserSerializer, NoteSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from redis_cache.cache_utils.user import UserProfileCache
import logging
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

logger = logging.getLogger(__name__)


class MyTokenObtainPairView(TokenObtainPairView):
    @classmethod
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            tokens = response.data

            access_token = tokens['access']
            refresh_token = tokens['refresh']

            res = Response()

            res_data = {'success':True}

            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='None',
                max_age=3600,  # 1 hour
                path='/'
            )

            res.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=True,
                samesite='None',
                max_age=3600,  # 1 hour
                path='/'
            )

            return res

        except:
            res_data = {'success':False}


class MyRefreshTokenView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')

            request.data['refresh'] = refresh_token

            response = super().post(request, *args, **kwargs)

            tokens = response.data
            access_token = tokens['access']

            res = Response()

            res.data = {'refreshed':True}

            res.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=True,
                samesite='None',
                max_age=3600,  # 1 hour
                path='/'
            )

            return res
        
        except:
            return Response({'refreshed':False})    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout endpoint that clears JWT cookies and user cache
    """
    
    response = Response({'message': 'Logout successful'})
    
    # Clear the access token cookie
    response.delete_cookie(
        'access_token',
        path='/',
        samesite='Lax'
    )
    
    # Clear the refresh token cookie
    response.delete_cookie(
        'refresh_token',
        path='/',
        samesite='Lax'
    )
    
    return response


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_authenticated(request):
    """
    Simple endpoint to verify if the user is authenticated.
    Returns 200 if authenticated, 401 if not.
    """
    return Response({"authenticated": True}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notes(request):
    user = request.user
    notes = Note.objects.filter(owner=user)
    serializer=NoteSerializer(notes, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register new user and set JWT cookies
    """
    data = request.data
    
    # Check required fields
    required_fields = ['username', 'email', 'password', 'first_name', 'last_name']
    for field in required_fields:
        if not data.get(field):
            return Response({
                'error': f'{field} is required'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if username already exists
    if User.objects.filter(username=data['username']).exists():
        return Response({
            'error': 'Username already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if email already exists
    if User.objects.filter(email=data['email']).exists():
        return Response({
            'error': 'Email already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Validate password
        validate_password(data['password'])
        
        # Create user
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data.get('phone_number', ''),  # Optional field
            is_verified=False  # Default to unverified
        )
        
        # Log the registration
        LoginHistory.objects.create(
            user=user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            status=True
        )
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Create response with user data
        response = Response({
            'user': UserSerializer(user).data,
            'message': 'Registration successful'
        })
        
        # Set refresh token cookie (7 days)
        response.set_cookie(
            'refresh_token',
            refresh_token,
            max_age=7*24*60*60,  # 7 days
            httponly=True,
            path='/',
            samesite='Lax'
        )
        
        # Set access token cookie (1 hour)
        response.set_cookie(
            'access_token',
            access_token,
            max_age=60*60,  # 1 hour
            httponly=True,
            path='/',
            samesite='Lax'
        )
        
        return response
    
    except ValidationError as e:
        return Response({
            'error': list(e.messages)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Custom login view that returns JWT tokens in cookies
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Please provide both username and password'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)
    
    if not user:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    try:
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Create response with user data
        response = Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        })
        
        # Set refresh token cookie (7 days)
        response.set_cookie(
            'refresh_token',
            refresh_token,
            max_age=7*24*60*60,  # 7 days
            httponly=True,
            path='/',
            samesite='Lax'
        )
        
        # Set access token cookie (1 hour)
        response.set_cookie(
            'access_token',
            access_token,
            max_age=60*60,  # 1 hour
            httponly=True,
            path='/',
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response(
            {'error': 'Login failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Profile endpoint that returns user data
    """
    try:
        user = request.user
        user_data = UserSerializer(user).data
        
        return Response({
            'user': user_data
        })
        
    except Exception as e:
        return Response({
            'error': f'Error retrieving profile data: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
