from django.urls import path
from .views import (
    register_by_emp_id,
    get_employee_info,
    login,
    admin_login,
    admin_list_users,
    admin_user_detail,
    admin_all_users_detail,
    admin_delete_user,
    upload_user_image,
    save_annotations,
    train_model,
    detect_defect_image,
    detect_defect_video,
    detect_defect_live,
    list_image_detection_results,
    list_video_detection_results,
    stop_live_detection,
    generate_batch_id,
    analysis_dashboard,
    total_annotated_images,
    defects_by_date,
    login_details,
    get_industries_list,  # New API
    set_user_industry,    # New API
    consolidate_and_train,  # New API
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# URL patterns for the Seamguard API
urlpatterns = [
    # JWT Token Endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User Registration and Employee Info
    path('register/employee/<str:emp_id>/', get_employee_info, name='get_employee_info'),
    path('register/', register_by_emp_id, name='register_by_emp_id'),

    # Authentication Endpoints
    path('login/', login, name='login'),
    path('admin/login/', admin_login, name='admin_login'),

    # Admin User Management Endpoints
    path('admin/users/list/', admin_list_users, name='admin_list_users'),
    path('admins/users/<str:emp_id>/', admin_user_detail, name='admin_user_detail'),
    path('admin/users/all/', admin_all_users_detail, name='admin_all_users_detail'),
    path('admin/users/<str:emp_id>/delete/', admin_delete_user, name='admin_delete_user'),

    # Training and Annotation Endpoints
    path('training/upload-image/', upload_user_image, name='upload_user_image'),
    path('training/save-annotations/', save_annotations, name='save_annotations'),
    path('training/train-model/', train_model, name='train_model'),

    # Detection Endpoints
    path('detection/image/', detect_defect_image, name='detect_defect_image'),
    path('detection/defect/image/', list_image_detection_results, name='list_image_detection_results'),
    path('detection/video/', detect_defect_video, name='detect_defect_video'),
    path('detection/defect/video/', list_video_detection_results, name='list_video_detection_results'),
    path('detection/generate_batch_id/', generate_batch_id, name='generate_batch_id'),
    path('detection/detect_defect_live/', detect_defect_live, name='detect_defect_live'),
    path('detection/stop_live_detection/', stop_live_detection, name='stop_live_detection'),

    # Dashboard and Analytics Endpoints
    path('dashboard/analysis/', analysis_dashboard, name='analysis_dashboard'),
    path('dashboard/total_annotated_images/', total_annotated_images, name='total_annotated_images'),
    path('dashboard/defects_by_date/', defects_by_date, name='defects_by_date'),
    path('dashboard/login_details/', login_details, name='login_details'),

    # New Industry and Training Endpoints
    path('industries/list/', get_industries_list, name='get_industries_list'),
    path('industries/set/', set_user_industry, name='set_user_industry'),
    path('training/consolidate-and-train/', consolidate_and_train, name='consolidate_and_train'),
]