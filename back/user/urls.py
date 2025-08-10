from django.urls import path
from .views import (
    MyTokenObtainPairView,
    MyRefreshTokenView,
    register_view,
    login_view,
    logout_view,
    get_authenticated,
    get_notes,
    profile_view
)

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', MyRefreshTokenView.as_view(), name='token_refresh'),
    path('notes/', get_notes, name='get_notes'),
    path('authenticated_user/', get_authenticated, name='get_authenticated')
]