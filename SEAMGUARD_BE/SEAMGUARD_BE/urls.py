from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Employee Registration API",
        default_version='v1',
        description="Register employees using external DB via emp_id",
        # Define security scheme for JWT
        security_definitions={
            'BearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT',
            }
        },
        security=[{'BearerAuth': []}],  # Apply BearerAuth globally or to specific endpoints
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    authentication_classes=[],
)

urlpatterns = [
    path('seamguard/', include("seamguard.urls")),  
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)