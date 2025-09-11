from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import register, login, predict, activity_log

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('predict/', predict, name='predict'),
    path('activity-log/', activity_log, name='activity_log'),
    # path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]