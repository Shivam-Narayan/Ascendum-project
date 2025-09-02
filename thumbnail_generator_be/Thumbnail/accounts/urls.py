from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path ('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name= 'logout'),
    path('generate-thumbnails/', views.generate_thumbnails_api, name='generate thumbnails'),
    path('enhanceThumbnails/', views.enhance_thumbnails, name='enhance thumbnails'),
    path('singleUpscale/', views.upscale_image, name='upscale_image'),
    path('multiUpscale/', views.upscale_images, name='upscale_images'),
    path('enhance_thumbnailhdr/', views.enhance_thumbnailhdr, name='enhance_thumbnailhdr')
    
    # path('thumbnails/<str:filename>/', views.serve_thumbnail, name='serve_thumbnail'),  # Add this line
    # path('secure-data/', views.protected_api),
    # path('logout/', views.logout_view, name='logout')

    # path('login1/', views2.login, name='login')
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)