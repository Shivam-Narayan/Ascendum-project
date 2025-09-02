from django.contrib import admin
from django.urls import include, path
from agrovet.swagger import schema_view
from agrovet.views import login, register



urlpatterns = [
    path('user/', include("agrovet.urls")),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]