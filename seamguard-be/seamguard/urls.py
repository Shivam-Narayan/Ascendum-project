from django.urls import path
from .views import (
    register_by_emp_id, get_employee_info, login, upload_user_image, save_annotations,
    train_model, detect_defect_image, detect_defect_video, detect_defect_live,
    list_image_detection_results, analysis_dashboard, total_annotated_images,
    defects_by_date, login_details, list_video_detection_results, stop_live_detection,
     admin_login, admin_list_users, admin_user_detail, admin_all_users_detail, admin_delete_user, generate_batch_id
    
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/employee/<str:emp_id>', get_employee_info, name='get_employee_info'),
    path('register', register_by_emp_id, name='register_by_emp_id'),
    path('login', login, name='login'),
    path('admin/login', admin_login, name='admin_login'),
    path('admin/users/list', admin_list_users, name='admin_list_users'),
    path('admin/seamguard/admin/user/<str:emp_id>/', admin_user_detail, name='admin_user_detail'),
    path('admin/users/all', admin_all_users_detail, name='admin_all_users_detail'),  
    path('admin/users/<str:emp_id>/delete', admin_delete_user, name='admin_delete_user'),
    path('training/upload-image', upload_user_image, name='upload_user_image'),
    path('training/save-annotations', save_annotations, name='save_annotations'),
    path('training/train-model', train_model, name='train_model'),
    path('detection/image', detect_defect_image, name='detect_defect_image'),
    path('detection/defect/image', list_image_detection_results, name='list_detection_results'),
    path('detection/video', detect_defect_video, name='detect_defect_video'),
    path('dashboard/analysis_dashboard/', analysis_dashboard, name='analysis_dashboard'),
    path('dashboard/total_annotated_images/', total_annotated_images, name='total_annotated_images'),
    path('dashboard/defects_by_date/', defects_by_date, name='defects_by_date'),
    path('dashboard/login_details/', login_details, name='login_details'),
    path('detection/defect/video/', list_video_detection_results, name='list_video_detection_results'),
    path('detection/stop_live_detection/', stop_live_detection, name='stop_live_detection'),
    path('detection/generate_batch_id/', generate_batch_id, name='generate_batch_id'),
    path('detection/detect_defect_live', detect_defect_live, name='detect_defect_live'),
   
]