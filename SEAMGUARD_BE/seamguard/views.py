from rest_framework.decorators import api_view, permission_classes, parser_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Dashboard, DashboardImage, Annotation, DetectionResult, LoginHistory, User
from .serializers import (
    LoginSerializer, DashboardSerializer, ErrorResponseSerializer,
    EmployeeMasterSerializer, RegisterUserFromEmpIDSerializer, UserSerializer
)
from django.http import JsonResponse
from django.db import connection
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import os, cv2, uuid, tempfile, logging, shutil, json, datetime
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from ultralytics import YOLO
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.exceptions import AuthenticationFailed
from django.utils.dateparse import parse_date
from collections import Counter
import base64
import redis
import numpy as np
import yaml

# Initialize Redis client
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Configure logging
logger = logging.getLogger(__name__)
model = YOLO(r"C:\Users\pathalamm\Desktop\Seamguard_be\best.pt")

# Industry list
industries = [
    "Glass", "Iron & Steel", "FMCG", "IT Hardware", "Automobiles",
    "Apparels", "Textiles", "Furnitures", "Leather", "Fabricated Metals", "CAD"
]

class DashboardUser:
    """Wrapper class to add authentication attributes to Dashboard model"""
    def __init__(self, dashboard_obj):
        self.dashboard_obj = dashboard_obj
        
    def __getattr__(self, attr):
        return getattr(self.dashboard_obj, attr)
        
    @property
    def is_authenticated(self):
        return True
        
    @property
    def is_anonymous(self):
        return False

    @property
    def is_admin(self):
        return False

class AdminUser:
    """Wrapper class for admin users"""
    def __init__(self, emp_id):
        self.emp_id = emp_id
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_admin = True

class DashboardJWTAuthentication(JWTAuthentication):
    """
    Custom authentication that verifies users against Dashboard table only
    and provides proper authentication attributes
    """
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user_id = validated_token.get('user_id')
            is_admin = validated_token.get('is_admin', False)
            if not user_id:
                raise AuthenticationFailed('user_id not found in token', code='invalid_token')

            if is_admin and str(user_id).startswith('admin_'):
                admin_emp_id = user_id[6:]
                return (AdminUser(admin_emp_id), validated_token)
            else:
                dashboard_user = Dashboard.objects.filter(id=user_id).first()
                if not dashboard_user:
                    raise AuthenticationFailed('Dashboard user not found', code='user_not_found')
                
                return (DashboardUser(dashboard_user), validated_token)
        except Exception as e:
            raise AuthenticationFailed(str(e))

def load_admins():
    admins_path = os.path.join(settings.BASE_DIR, 'admins.json')
    if os.path.exists(admins_path):
        with open(admins_path, 'r') as f:
            return json.load(f)
    return []

################## Employee Info by emp_id (API) ####################
@swagger_auto_schema(
    method='get',
    operation_summary="Get employee info by emp_id",
    manual_parameters=[
        openapi.Parameter(
            name='emp_id',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            required=True,
            description='Employee ID to fetch information for'
        ),
    ],
    responses={
        200: EmployeeMasterSerializer(),
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_employee_info(request, emp_id):
    if not emp_id:
        return Response(ErrorResponseSerializer({'error': 'emp_id is required'}).data, status=status.HTTP_400_BAD_REQUEST)
 
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT emp_id, name, line_number, department, phone_number, email, industry FROM seamguard_employeemaster WHERE emp_id = %s",
            [emp_id]
        )
        row = cursor.fetchone()
        if row:
            emp_data = {
                "emp_id": row[0],
                "name": row[1],
                "line_number": row[2],
                "department": row[3],
                "phone_number": row[4],
                "email": row[5],
                "industry": row[6]
            }
            return JsonResponse(emp_data, status=200)
        return Response(ErrorResponseSerializer({'error': 'Employee not found'}).data, status=status.HTTP_404_NOT_FOUND)

################## Register API ####################
@swagger_auto_schema(
    method='post',
    request_body=RegisterUserFromEmpIDSerializer,
    responses={
        201: openapi.Response(
            description="User registered successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'emp_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'name': openapi.Schema(type=openapi.TYPE_STRING),
                    'email': openapi.Schema(type=openapi.TYPE_STRING),
                    'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                    'industry': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: ErrorResponseSerializer
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_by_emp_id(request):
    serializer = RegisterUserFromEmpIDSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        Dashboard.objects.create(
            emp_id=user.emp_id,
            name=user.name,
            email=user.email,
            phone_number=user.phone_number,
            line_number=user.line_number,
            department=user.department,
            industry=user.industry,  # Use industry from user
            password=user.password
        )
        return Response({
            "message": "User registered successfully",
            "data": {
                "emp_id": user.emp_id,
                "name": user.name,
                "email": user.email,
                "phone_number": user.phone_number,
                "industry": user.industry
            }
        }, status=status.HTTP_201_CREATED)
    return Response(ErrorResponseSerializer({'error': serializer.errors}).data, status=status.HTTP_400_BAD_REQUEST)

################## Login API ####################
@swagger_auto_schema(
    method='post',
    request_body=LoginSerializer,
    responses={
        200: openapi.Response(
            description="Login successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'emp_id': openapi.Schema(type=openapi.TYPE_STRING),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'email': openapi.Schema(type=openapi.TYPE_STRING),
                            'phone_number': openapi.Schema(type=openapi.TYPE_STRING),
                            'line_number': openapi.Schema(type=openapi.TYPE_STRING),
                            'department': openapi.Schema(type=openapi.TYPE_STRING),
                            'industry': openapi.Schema(type=openapi.TYPE_STRING)
                        }
                    )
                }
            )
        ),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
        404: ErrorResponseSerializer
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(ErrorResponseSerializer({'error': serializer.errors}).data, status=status.HTTP_400_BAD_REQUEST)
    
    user = serializer.validated_data['user']
    dashboard_user = Dashboard.objects.filter(emp_id=user.emp_id).first()
    if not dashboard_user:
        return Response(
            ErrorResponseSerializer({'error': 'Dashboard user not found for this account'}).data,
            status=status.HTTP_404_NOT_FOUND
        )
    # Log the login
    LoginHistory.objects.create(user=dashboard_user)
    token = AccessToken.for_user(dashboard_user)
    
    return Response({
        'token': str(token),
        'user': DashboardSerializer(dashboard_user).data
    }, status=status.HTTP_200_OK)

################## Admin Login API ####################
@swagger_auto_schema(
    method='post',
    operation_summary="Admin login",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['emp_id', 'password'],
        properties={
            'emp_id': openapi.Schema(type=openapi.TYPE_STRING),
            'password': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: openapi.Response(
            description="Admin login successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'token': openapi.Schema(type=openapi.TYPE_STRING),
                    'emp_id': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def admin_login(request):
    emp_id = request.data.get('emp_id')
    password = request.data.get('password')
    if not emp_id or not password:
        return Response(ErrorResponseSerializer({'error': 'emp_id and password are required'}).data, status=status.HTTP_400_BAD_REQUEST)
    
    admins = load_admins()
    admin = next((a for a in admins if a['emp_id'] == emp_id and a['password'] == password), None)
    if not admin:
        return Response(ErrorResponseSerializer({'error': 'Invalid admin credentials'}).data, status=status.HTTP_401_UNAUTHORIZED)
    
    token = AccessToken()
    token['user_id'] = 'admin_' + emp_id
    token['is_admin'] = True
    
    return Response({
        'token': str(token),
        'emp_id': emp_id
    }, status=status.HTTP_200_OK)

################## Upload User Image API ####################
@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('images', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True, description='One or more image files to upload', multiple=True),
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
    ],
    responses={
        200: openapi.Response(
            description="Images uploaded successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'images': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'image_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'image_url': openapi.Schema(type=openapi.TYPE_STRING),
                                'image_name': openapi.Schema(type=openapi.TYPE_STRING),
                                'industry': openapi.Schema(type=openapi.TYPE_STRING)
                            }
                        )
                    )
                }
            )
        ),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
    security=[{'BearerAuth': []}]
)
@api_view(['POST'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_user_image(request):
    images = request.FILES.getlist('images')
    if not images:
        return Response(ErrorResponseSerializer({'error': 'At least one image is required'}).data, status=status.HTTP_400_BAD_REQUEST)

    try:
        dashboard_user = request.user.dashboard_obj
        emp_id = dashboard_user.emp_id
        industry = dashboard_user.industry
        if not industry:
            return Response(ErrorResponseSerializer({'error': 'User must have an industry assigned'}).data, status=status.HTTP_400_BAD_REQUEST)

        uploaded_images = []
        for image in images:
            dashboard_image = DashboardImage.objects.create(
                dashboard_user=dashboard_user,
                emp_id=emp_id,
                image=image,
                industry=industry
            )

            image_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, dashboard_image.image.name)).replace('\\', '/')
            logger.debug(f"Saving image to: {image_path}")
            if not os.path.exists(image_path):
                logger.error(f"Failed to save image: {image_path}")
                dashboard_image.delete()
                continue

            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"Failed to read image: {image_path}")
                dashboard_image.delete()
                continue

            image_url = request.build_absolute_uri(dashboard_image.image.url)
            image_name = dashboard_image.image.name
            uploaded_images.append({
                'image_id': dashboard_image.id,
                'image_url': image_url,
                'image_name': image_name,
                'industry': industry
            })
            logger.info(f"Image uploaded successfully: image_id={dashboard_image.id}, url={image_url}, name={image_name}, industry={industry}")

        if not uploaded_images:
            return Response(ErrorResponseSerializer({'error': 'No valid images uploaded'}).data, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': 'Images uploaded successfully',
            'images': uploaded_images
        }, status=status.HTTP_200_OK)
    except AttributeError:
        logger.error(f"Authentication error: User data not found")
        return Response(ErrorResponseSerializer({'error': 'User authentication data not found'}).data, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Error uploading images for emp_id {emp_id}: {str(e)}")
        return Response(ErrorResponseSerializer({'error': str(e)}).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################## Annotation API ####################
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['image_id', 'annotations'],
        properties={
            'image_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'annotations': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'class_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'x_min': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'y_min': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'x_max': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'y_max': openapi.Schema(type=openapi.TYPE_NUMBER),
                    }
                )
            )
        }
    ),
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
    ],
    responses={
        200: openapi.Response(description="Annotations saved successfully"),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
        404: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['POST'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def save_annotations(request):
    user = request.user
    image_id = request.data.get('image_id')
    annotations = request.data.get('annotations', [])

    if not image_id or not annotations:
        logger.error(f"Missing image_id or annotations: image_id={image_id}, annotations={annotations}")
        return Response(ErrorResponseSerializer({'error': 'image_id and annotations are required'}).data, status=status.HTTP_400_BAD_REQUEST)

    try:
        image = DashboardImage.objects.get(id=image_id, dashboard_user=user.dashboard_obj)
    except DashboardImage.DoesNotExist:
        logger.error(f"Image not found for image_id: {image_id}")
        return Response(ErrorResponseSerializer({'error': 'Image not found or not authorized'}).data, status=status.HTTP_404_NOT_FOUND)

    try:
        for ann in annotations:
            if not all(key in ann for key in ['class_name', 'x_min', 'y_min', 'x_max', 'y_max']):
                logger.error(f"Invalid annotation format: {ann}")
                return Response(ErrorResponseSerializer({'error': 'Invalid annotation format'}).data, status=status.HTTP_400_BAD_REQUEST)
            Annotation.objects.create(
                user=user.dashboard_obj,
                image=image,
                class_name=ann['class_name'],
                x_min=float(ann['x_min']),
                y_min=float(ann['y_min']),
                x_max=float(ann['x_max']),
                y_max=float(ann['y_max']),
                industry=image.industry
            )
        logger.info(f"Saved {len(annotations)} annotations for image_id: {image_id}, industry: {image.industry}")
        return Response({'message': 'Annotations saved successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error saving annotations for image_id {image_id}: {str(e)}")
        return Response(ErrorResponseSerializer({'error': str(e)}).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################## Train Model API ####################
@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['epochs'],
        properties={
            'epochs': openapi.Schema(type=openapi.TYPE_INTEGER),
        }
    ),
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
    ],
    responses={
        200: openapi.Response(
            description="Dataset preparation complete",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'yaml_path': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['POST'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def train_model(request):
    try:
        dashboard_user = request.user.dashboard_obj
        emp_id = dashboard_user.emp_id
        industry = dashboard_user.industry
        if not industry:
            return Response(ErrorResponseSerializer({'error': 'User must have an industry assigned'}).data, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Starting dataset preparation for user: {emp_id}, industry: {industry}")
        try:
            epochs = int(request.data.get('epochs', 10))
        except ValueError:
            logger.error(f"Invalid epochs value: {request.data.get('epochs')}")
            return Response(ErrorResponseSerializer({'error': 'epochs must be an integer'}).data, status=status.HTTP_400_BAD_REQUEST)

        annotations = Annotation.objects.filter(user=dashboard_user, industry=industry)
        if not annotations:
            logger.error(f"No annotations found for user: {emp_id}, industry: {industry}")
            return Response(ErrorResponseSerializer({'error': 'No annotations found for user in this industry'}).data, status=status.HTTP_400_BAD_REQUEST)

        user_folder = os.path.normpath(os.path.join(settings.MEDIA_ROOT, 'yolo_datasets', emp_id, str(uuid.uuid4()))).replace('\\', '/')
        os.makedirs(user_folder, exist_ok=True)

        train_images_dir = os.path.normpath(os.path.join(user_folder, 'images', 'train')).replace('\\', '/')
        train_labels_dir = os.path.normpath(os.path.join(user_folder, 'labels', 'train')).replace('\\', '/')
        os.makedirs(train_images_dir, exist_ok=True)
        os.makedirs(train_labels_dir, exist_ok=True)

        class_names = sorted(set(ann.class_name for ann in annotations))
        class_to_id = {name: idx for idx, name in enumerate(class_names)}
        image_ids = set(ann.image_id for ann in annotations)
        logger.info(f"Found {len(image_ids)} unique images and {len(class_names)} classes for user {emp_id}, industry {industry}")

        valid_images = []
        for image in DashboardImage.objects.filter(id__in=image_ids, industry=industry):
            image_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, image.image.name)).replace('\\', '/')
            logger.debug(f"Processing image: {image_path} (image_id: {image.id})")
            if not os.path.exists(image_path):
                logger.warning(f"Image not found: {image_path} (image_id: {image.id})")
                continue

            img = cv2.imread(image_path)
            if img is None:
                logger.warning(f"Failed to read image: {image_path} (image_id: {image.id})")
                continue
            img_height, img_width = img.shape[:2]
            if img_height == 0 or img_width == 0:
                logger.warning(f"Invalid image dimensions for {image_path} (image_id: {image.id})")
                continue

            dest_image_path = os.path.normpath(os.path.join(train_images_dir, f"{image.id}.jpg")).replace('\\', '/')
            try:
                shutil.copyfile(image_path, dest_image_path)
                if not os.path.exists(dest_image_path):
                    logger.warning(f"Failed to copy image to: {dest_image_path} (image_id: {image.id})")
                    continue
            except Exception as e:
                logger.warning(f"Error copying image {image_path} (image_id: {image.id}): {str(e)}")
                continue

            label_path = os.path.normpath(os.path.join(train_labels_dir, f"{image.id}.txt")).replace('\\', '/')
            try:
                with open(label_path, 'w') as f:
                    image_annotations = annotations.filter(image=image)
                    if not image_annotations:
                        logger.warning(f"No annotations found for image_id: {image.id}")
                        continue
                    for ann in image_annotations:
                        x_center = (ann.x_min + ann.x_max) / 2 / img_width
                        y_center = (ann.y_min + ann.y_max) / 2 / img_height
                        width = (ann.x_max - ann.x_min) / img_width
                        height = (ann.y_max - ann.y_min) / img_height
                        if any(v <= 0 or v > 1 for v in [x_center, y_center, width, height]):
                            logger.warning(f"Invalid annotation coordinates for image_id {image.id}: {ann}")
                            continue
                        class_id = class_to_id[ann.class_name]
                        f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")
                valid_images.append(image.id)
                logger.debug(f"Created label file: {label_path} for image_id: {image.id}")
            except Exception as e:
                logger.warning(f"Error creating label file for image {image.id}: {str(e)}")
                continue

        if not valid_images:
            logger.error(f"No valid images found for training for user {emp_id}, industry {industry}")
            return Response(ErrorResponseSerializer({'error': 'No valid images found for training'}).data, status=status.HTTP_400_BAD_REQUEST)

        logger.info(f"Prepared {len(valid_images)} valid images for dataset")

        yaml_path = os.path.normpath(os.path.join(user_folder, 'data.yaml')).replace('\\', '/')
        with open(yaml_path, 'w') as f:
            f.write(f"""path: {user_folder}
train: images/train
val: images/train
nc: {len(class_names)}
names:
""")
            for idx, name in enumerate(class_names):
                f.write(f"  {idx}: {name}\n")
        logger.debug(f"Created data.yaml: {yaml_path}")

        if not os.path.exists(yaml_path):
            logger.error(f"YAML file not found: {yaml_path}")
            return Response(ErrorResponseSerializer({'error': 'Failed to create YAML file'}).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        logger.info(f"Dataset preparation completed successfully for user {emp_id}, YAML saved to {yaml_path}")

        redis_client.lpush(f"industry_yaml:{industry}", yaml_path)
        logger.info(f"Stored YAML path for industry {industry}: {yaml_path}")

        return Response({
            'message': 'Dataset preparation complete',
            'yaml_path': yaml_path
        }, status=status.HTTP_200_OK)

    except AttributeError:
        logger.error(f"Authentication error: User data not found")
        return Response(ErrorResponseSerializer({'error': 'User authentication data not found'}).data, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Dataset preparation failed for user {emp_id}: {str(e)}")
        return Response(ErrorResponseSerializer({'error': f'Dataset preparation failed: {str(e)}'}).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################## Detect Image Post API ####################
@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'image', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True,
            description='Image file(s) to annotate (multiple files allowed for batch upload)'
        ),
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
    ],
    responses={
        200: openapi.Response(
            description="Annotated image(s) result",
            content={'application/json': {}}
        ),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
        404: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['POST'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def detect_defect_image(request):
    images = request.FILES.getlist('image')
    if not images:
        return Response(
            ErrorResponseSerializer({'error': 'Image file required'}).data,
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        dashboard_user = request.user.dashboard_obj
        emp_id = dashboard_user.emp_id
        industry = dashboard_user.industry
        if not industry:
            return Response(ErrorResponseSerializer({'error': 'User must have an industry assigned'}).data, status=status.HTTP_400_BAD_REQUEST)

        batch_id = str(uuid.uuid4())
        tmp_paths = []
        results_list = []

        model_path = os.path.join(settings.BASE_DIR, f"{industry}_model.pt")
        local_model = YOLO(model_path) if os.path.exists(model_path) else model

        for idx, image_file in enumerate(images):
            dashboard_image = DashboardImage.objects.create(
                dashboard_user=dashboard_user,
                emp_id=emp_id,
                image=image_file,
                industry=industry
            )

            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                for chunk in image_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
            tmp_paths.append(tmp_path)

            results = local_model(tmp_path)
            annotated_img = results[0].plot()

            detected_defects = []
            for result in results:
                for box in result.boxes:
                    defect = {
                        'class': result.names[int(box.cls)],
                        'confidence': float(box.conf),
                        'bbox': {
                            'x1': float(box.xyxy[0][0]),
                            'y1': float(box.xyxy[0][1]),
                            'x2': float(box.xyxy[0][2]),
                            'y2': float(box.xyxy[0][3])
                        }
                    }
                    detected_defects.append(defect)

            DetectionResult.objects.create(
                dashboard_user=dashboard_user,
                emp_id=emp_id,
                image_id=dashboard_image,
                defect_result=json.dumps(detected_defects),
                source='image',
                batch_id=batch_id,
                industry=industry
            )

            result_dir = os.path.join('image_results', batch_id).replace('\\', '/')
            full_result_dir = os.path.join(settings.MEDIA_ROOT, result_dir)
            os.makedirs(full_result_dir, exist_ok=True)

            frame_filename = f"annotated_{idx}.jpg"
            frame_path = os.path.join(result_dir, frame_filename).replace('\\', '/')
            default_storage.save(frame_path, ContentFile(cv2.imencode('.jpg', annotated_img)[1].tobytes()))

            frame_url = request.build_absolute_uri(f'/media/{frame_path}')
            results_list.append({
                'original_url': request.build_absolute_uri(dashboard_image.image.url),
                'annotated_url': frame_url,
                'class_names': [d['class'] for d in detected_defects],
                'industry': industry
            })

        for path in tmp_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except PermissionError:
                    logger.warning(f"Could not delete temporary file {path} due to PermissionError")

        return Response({
            'batch_id': batch_id,
            'results': results_list
        }, status=status.HTTP_200_OK)

    except AttributeError:
        return Response(
            ErrorResponseSerializer({'error': 'User authentication data not found'}).data,
            status=status.HTTP_401_UNAUTHORIZED
        )
    except Exception as e:
        for path in tmp_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except PermissionError:
                    logger.warning(f"Could not delete temporary file {path} due to PermissionError")
        return Response(
            ErrorResponseSerializer({'error': str(e)}).data,
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

################## Detect Image Get API ####################
@swagger_auto_schema(
    method='get',
    operation_summary="List detection results for the authenticated employee's latest image upload",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
        openapi.Parameter(
            name='batch_id',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description='Batch ID to filter results (defaults to latest batch if not provided)'
        ),
    ],
    responses={
        200: openapi.Response(
            description="List of detection results with class names, image URLs, and source",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'class_names': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            description='List of defect class names'
                        ),
                        'image_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the original image'),
                        'source': openapi.Schema(type=openapi.TYPE_STRING, description='Source of detection (image)'),
                        'industry': openapi.Schema(type=openapi.TYPE_STRING, description='Industry of the detection')
                    }
                )
            )
        ),
        401: ErrorResponseSerializer,
        404: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['GET'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def list_image_detection_results(request):
    try:
        dashboard_user = request.user.dashboard_obj
        emp_id = dashboard_user.emp_id
        industry = dashboard_user.industry

        results_qs = DetectionResult.objects.filter(emp_id=emp_id, source='image', industry=industry)
        batch_id = request.GET.get('batch_id')
        if batch_id:
            results_qs = results_qs.filter(batch_id=batch_id)
        else:
            latest = results_qs.order_by('-created_at').first()
            if latest:
                results_qs = results_qs.filter(batch_id=latest.batch_id)
            else:
                return Response([], status=status.HTTP_200_OK)

        response_data = [
            {
                'class_names': [defect['class'] for defect in json.loads(result.defect_result)] if result.defect_result else [],
                'image_url': request.build_absolute_uri(result.image_id.image.url) if result.image_id and result.image_id.image else None,
                'source': result.source,
                'industry': result.industry
            }
            for result in results_qs
        ]
        return Response(response_data, status=status.HTTP_200_OK)

    except AttributeError:
        return Response(ErrorResponseSerializer({'error': 'User authentication data not found'}).data, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response(ErrorResponseSerializer({'error': str(e)}).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



################## Detect Video API ####################
@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter('video', openapi.IN_FORM, type=openapi.TYPE_FILE, required=True, description='Video file to annotate'),
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
    ],
    responses={
        200: openapi.Response(
            description="List of annotated frames with defects",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'results_url': openapi.Schema(type=openapi.TYPE_STRING),
                    'total_frames': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'defective_frames': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'saved_frames': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_STRING)),
                    'batch_id': openapi.Schema(type=openapi.TYPE_STRING),
                    'industry': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['POST'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def detect_defect_video(request):
    video_file = request.FILES.get('video')
    if not video_file:
        return Response(ErrorResponseSerializer({'error': 'Video file required'}).data, status=status.HTTP_400_BAD_REQUEST)

    try:
        dashboard_user = request.user.dashboard_obj
        emp_id = dashboard_user.emp_id
        industry = dashboard_user.industry
        if not industry:
            return Response(ErrorResponseSerializer({'error': 'User must have an industry assigned'}).data, status=status.HTTP_400_BAD_REQUEST)

        batch_id = str(uuid.uuid4())
        model_path = os.path.join(settings.BASE_DIR, f"{industry}_model.pt")
        local_model = YOLO(model_path) if os.path.exists(model_path) else model

        result_dir = os.path.join('defect_results', batch_id).replace('\\', '/')
        full_result_dir = os.path.join(settings.MEDIA_ROOT, result_dir)
        os.makedirs(full_result_dir, exist_ok=True)

        if not full_result_dir.startswith(os.path.normpath(settings.MEDIA_ROOT)):
            return Response(ErrorResponseSerializer({'error': 'Invalid file path'}).data, status=status.HTTP_400_BAD_REQUEST)

        input_path = None
        cap = None
        saved_frames = []

        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                for chunk in video_file.chunks():
                    tmp.write(chunk)
                input_path = tmp.name

            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                return Response(ErrorResponseSerializer({'error': 'Could not open video file'}).data, status=status.HTTP_400_BAD_REQUEST)

            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_skip = max(1, int(fps / 2))

            defective_frames = 0
            frame_number = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_number % frame_skip != 0:
                    frame_number += 1
                    continue

                model_results = local_model(frame)
                detected_defects = []

                for result in model_results:
                    for box in result.boxes:
                        defect = {
                            'class': result.names[int(box.cls)],
                            'confidence': float(box.conf),
                            'bbox': {
                                'x1': float(box.xyxy[0][0]),
                                'y1': float(box.xyxy[0][1]),
                                'x2': float(box.xyxy[0][2]),
                                'y2': float(box.xyxy[0][3])
                            }
                        }
                        detected_defects.append(defect)

                if detected_defects:
                    defective_frames += 1
                    annotated_frame = model_results[0].plot()
                    frame_filename = f"frame_{frame_number}.jpg"
                    frame_path = os.path.join(result_dir, frame_filename).replace('\\', '/')
                    full_frame_path = os.path.join(settings.MEDIA_ROOT, frame_path)

                    _, buffer = cv2.imencode('.jpg', annotated_frame)
                    default_storage.save(frame_path, ContentFile(buffer.tobytes()))

                    if os.path.exists(full_frame_path):
                        frame_url = request.build_absolute_uri(f'/media/{frame_path}')
                        saved_frames.append(frame_url)
                        logger.debug(f"Saved frame: {full_frame_path} (URL: {frame_url})")

                        dashboard_image = DashboardImage.objects.create(
                            dashboard_user=dashboard_user,
                            emp_id=emp_id,
                            image=frame_path,
                            industry=industry
                        )

                        DetectionResult.objects.create(
                            dashboard_user=dashboard_user,
                            emp_id=emp_id,
                            image_id=dashboard_image,
                            defect_result=json.dumps(detected_defects),
                            source='video',
                            batch_id=batch_id,
                            industry=industry
                        )
                    else:
                        logger.warning(f"Failed to save frame: {full_frame_path}")

                frame_number += 1

            if defective_frames == 0:
                return Response({
                    'message': 'No defects found in video',
                    'total_frames': total_frames,
                    'defective_frames': 0,
                    'saved_frames': saved_frames,
                    'batch_id': batch_id,
                    'industry': industry
                }, status=status.HTTP_200_OK)

            results_url = request.build_absolute_uri(f'/media/{result_dir}/')
            return Response({
                'results_url': results_url,
                'total_frames': total_frames,
                'defective_frames': defective_frames,
                'saved_frames': saved_frames,
                'batch_id': batch_id,
                'industry': industry
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing video: {str(e)}")
            return Response(ErrorResponseSerializer({'error': str(e)}).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            if cap is not None:
                cap.release()
            if input_path is not None and os.path.exists(input_path):
                try:
                    os.remove(input_path)
                except PermissionError:
                    logger.warning(f"Could not delete temporary file {input_path} due to PermissionError")

    except AttributeError:
        return Response(ErrorResponseSerializer({'error': 'User authentication data not found'}).data, status=status.HTTP_401_UNAUTHORIZED)



################## Detect Video Get API ####################
@swagger_auto_schema(
    method='get',
    operation_summary="List video detection results for the authenticated employee's latest video upload",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
        openapi.Parameter(
            name='batch_id',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description='Batch ID to filter results (defaults to latest batch if not provided)'
        ),
    ],
    responses={
        200: openapi.Response(
            description="List of video detection results with class names, image URLs, and source",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'class_names': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            description='List of defect class names'
                        ),
                        'image_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the video frame image'),
                        'source': openapi.Schema(type=openapi.TYPE_STRING, description='Source of detection (video)'),
                        'industry': openapi.Schema(type=openapi.TYPE_STRING, description='Industry of the detection')
                    }
                )
            )
        ),
        401: ErrorResponseSerializer,
        404: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['GET'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def list_video_detection_results(request):
    try:
        dashboard_user = request.user.dashboard_obj
        emp_id = dashboard_user.emp_id
        industry = dashboard_user.industry

        results_qs = DetectionResult.objects.filter(emp_id=emp_id, source='video', industry=industry)
        batch_id = request.GET.get('batch_id')
        if batch_id:
            results_qs = results_qs.filter(batch_id=batch_id)
        else:
            latest = results_qs.order_by('-created_at').first()
            if latest:
                results_qs = results_qs.filter(batch_id=latest.batch_id)
            else:
                return Response([], status=status.HTTP_200_OK)

        response_data = [
            {
                'class_names': [defect['class'] for defect in json.loads(result.defect_result)] if result.defect_result else [],
                'image_url': request.build_absolute_uri(result.image_id.image.url) if result.image_id and result.image_id.image else None,
                'source': result.source,
                'industry': result.industry
            }
            for result in results_qs
        ]
        return Response(response_data, status=status.HTTP_200_OK)

    except AttributeError:
        return Response(ErrorResponseSerializer({'error': 'User authentication data not found'}).data, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response(ErrorResponseSerializer({'error': str(e)}).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################## Generate Batch ID API ####################
@swagger_auto_schema(
    method='get',
    operation_summary="Generate a new batch ID for live detection session",
    operation_description="Generates a unique batch ID for a new live detection session and initializes it in Redis. Requires JWT authentication.",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
    ],
    responses={
        200: openapi.Response(
            description="Successfully generated batch ID",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'batch_id': openapi.Schema(type=openapi.TYPE_STRING, description='Unique batch ID for the live detection session')
                }
            )
        ),
        401: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['GET'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def generate_batch_id(request):
    try:
        dashboard_user = request.user.dashboard_obj
        batch_id = str(uuid.uuid4())
        redis_client.set(f"live_session:{batch_id}", json.dumps([]))
        logger.info(f"Generated batch_id: {batch_id} for user: {dashboard_user.emp_id}")
        
        return Response({'batch_id': batch_id}, status=200)
        
    except AttributeError as e:
        logger.error(f"Authentication error: {str(e)}")
        return Response({'error': 'User authentication data not found'}, status=401)
    except Exception as e:
        logger.error(f"Failed to generate batch_id: {str(e)}")
        return Response({'error': f'Server error: {str(e)}'}, status=500)

################## Detect Defect Live API ####################
@swagger_auto_schema(
    method='post',
    operation_summary="Detect defects in a live image frame",
    operation_description="Processes a single base64-encoded image frame, runs defect detection using the model, and returns annotated image and defect details. Requires JWT authentication.",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['batch_id', 'image'],
        properties={
            'batch_id': openapi.Schema(type=openapi.TYPE_STRING, description='Batch ID for the live detection session'),
            'image': openapi.Schema(type=openapi.TYPE_STRING, description='Base64-encoded image data')
        }
    ),
    responses={
        200: openapi.Response(
            description="Successful defect detection",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'annotated_image': openapi.Schema(type=openapi.TYPE_STRING, description='Base64-encoded annotated image with detected defects'),
                    'defects': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'class': openapi.Schema(type=openapi.TYPE_STRING, description='Defect class name'),
                                'confidence': openapi.Schema(type=openapi.TYPE_NUMBER, description='Confidence score of the detection'),
                                'bbox': openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        'x1': openapi.Schema(type=openapi.TYPE_NUMBER, description='Top-left x coordinate'),
                                        'y1': openapi.Schema(type=openapi.TYPE_NUMBER, description='Top-left y coordinate'),
                                        'x2': openapi.Schema(type=openapi.TYPE_NUMBER, description='Bottom-right x coordinate'),
                                        'y2': openapi.Schema(type=openapi.TYPE_NUMBER, description='Bottom-right y coordinate')
                                    }
                                )
                            }
                        )
                    ),
                    'image_url': openapi.Schema(type=openapi.TYPE_STRING, description='URL of the saved annotated image', nullable=True),
                    'industry': openapi.Schema(type=openapi.TYPE_STRING, description='Industry of the detection')
                }
            )
        ),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['POST'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def detect_defect_live(request):
    try:
        dashboard_user = request.user.dashboard_obj
        emp_id = dashboard_user.emp_id
        industry = dashboard_user.industry
        if not industry:
            return Response(ErrorResponseSerializer({'error': 'User must have an industry assigned'}).data, status=status.HTTP_400_BAD_REQUEST)

        batch_id = request.data.get('batch_id')
        image_data = request.data.get('image')

        if not batch_id:
            return Response({'error': 'batch_id is required'}, status=400)
        if not image_data:
            return Response({'error': 'No image provided'}, status=400)

        if not redis_client.exists(f"live_session:{batch_id}"):
            return Response({'error': 'No active session found for this batch_id'}, status=404)

        if image_data.startswith("data:image"):
            image_data = image_data.split(",")[1]
        img_bytes = base64.b64decode(image_data)
        img_array = np.frombuffer(img_bytes, np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if frame is None:
            return Response({'error': 'Invalid image format'}, status=400)

        frame = cv2.resize(frame, (640, 480))

        model_path = os.path.join(settings.BASE_DIR, f"{industry}_model.pt")
        local_model = YOLO(model_path) if os.path.exists(model_path) else model

        model_results = local_model(frame)
        detected_defects = []

        for result in model_results:
            for box in result.boxes:
                defect = {
                    'class': result.names[int(box.cls)],
                    'confidence': float(box.conf),
                    'bbox': {
                        'x1': float(box.xyxy[0][0]),
                        'y1': float(box.xyxy[0][1]),
                        'x2': float(box.xyxy[0][2]),
                        'y2': float(box.xyxy[0][3])
                    }
                }
                detected_defects.append(defect)

        annotated_img = model_results[0].plot()
        _, jpeg_frame = cv2.imencode('.jpg', annotated_img)
        response_data = {
            'annotated_image': base64.b64encode(jpeg_frame.tobytes()).decode('utf-8'),
            'defects': detected_defects,
            'industry': industry
        }

        if detected_defects:
            frame_filename = f"live_frame_{uuid.uuid4().hex}.jpg"
            frame_dir = os.path.join('live_results', batch_id)
            os.makedirs(os.path.join(settings.MEDIA_ROOT, frame_dir), exist_ok=True)
            frame_path = os.path.join(frame_dir, frame_filename).replace('\\', '/')
            cv2.imwrite(os.path.join(settings.MEDIA_ROOT, frame_path), annotated_img)

            dashboard_image = DashboardImage.objects.create(
                dashboard_user=dashboard_user,
                emp_id=emp_id,
                image=frame_path,
                industry=industry
            )
            DetectionResult.objects.create(
                dashboard_user=dashboard_user,
                emp_id=emp_id,
                image_id=dashboard_image,
                defect_result=json.dumps(detected_defects),
                source='live',
                batch_id=batch_id,
                industry=industry
            )

            image_url = request.build_absolute_uri(dashboard_image.image.url)
            response_data['image_url'] = image_url

            session_data = json.loads(redis_client.get(f"live_session:{batch_id}") or "[]")
            session_data.append({
                'class_names': [d['class'] for d in detected_defects],
                'image_url': image_url,
                'source': 'live',
                'industry': industry
            })
            redis_client.set(f"live_session:{batch_id}", json.dumps(session_data))

        return Response(response_data, status=200)

    except AttributeError:
        return Response({'error': 'User authentication data not found'}, status=401)
    except Exception as e:
        logger.error(f"Error processing frame for batch_id {batch_id}: {str(e)}")
        return Response({'error': f'Server error: {str(e)}'}, status=500)

################## Stop Live Detection API ####################
@swagger_auto_schema(
    method='get',
    operation_summary="Stop a live detection session and retrieve results",
    operation_description="Stops a live detection session by batch ID and returns all defected images detected during the session. Requires JWT authentication.",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
        openapi.Parameter(
            name='batch_id',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=True,
            description='Batch ID of the live detection session to stop'
        ),
    ],
    responses={
        200: openapi.Response(
            description="List of defected images from the session",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'class_names': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING),
                            description='List of defect class names detected in the image'
                        ),
                        'image_url': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='URL of the annotated image',
                            nullable=True
                        ),
                        'source': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Source of the detection (e.g., live)'
                        ),
                        'industry': openapi.Schema(type=openapi.TYPE_STRING, description='Industry of the detection')
                    }
                )
            )
        ),
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['GET'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def stop_live_detection(request):
    batch_id = request.GET.get('batch_id')
    if not batch_id:
        return Response({'error': 'batch_id is required'}, status=400)

    if not redis_client.exists(f"live_session:{batch_id}"):
        return Response({'error': 'No active session found for this batch_id'}, status=404)

    try:
        defected_images = json.loads(redis_client.get(f"live_session:{batch_id}") or "[]")
        redis_client.delete(f"live_session:{batch_id}")
    except Exception as e:
        logger.error(f"Redis error for batch_id {batch_id}: {str(e)}")
        return Response({'error': f'Redis error: {str(e)}'}, status=500)

    response_data = [
        {
            "class_names": img.get("class_names", []),
            "image_url": img.get("image_url"),
            "source": img.get("source"),
            "industry": img.get("industry")
        }
        for img in defected_images
    ]

    return Response(response_data, status=status.HTTP_200_OK)

################## Analysis Dashboard API ####################
@swagger_auto_schema(
    method='get',
    operation_summary="Get analysis dashboard data for the authenticated user",
    manual_parameters=[
        openapi.Parameter(
            name='date',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description='Optional date filter (YYYY-MM-DD). If not provided, returns all data.'
        ),
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
    ],
    responses={
        200: openapi.Response(
            description="Analysis dashboard data",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'line_number': openapi.Schema(type=openapi.TYPE_STRING),
                    'department': openapi.Schema(type=openapi.TYPE_STRING),
                    'industry': openapi.Schema(type=openapi.TYPE_STRING),
                    'account_created_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                    'total_annotated_images': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'defects_found': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                                'detections': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    items=openapi.Items(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'time': openapi.Schema(type=openapi.TYPE_STRING, format='time'),
                                            'defect_result': openapi.Schema(type=openapi.TYPE_STRING),
                                            'source': openapi.Schema(type=openapi.TYPE_STRING),
                                            'industry': openapi.Schema(type=openapi.TYPE_STRING)
                                        }
                                    )
                                )
                            }
                        )
                    )
                }
            )
        ),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['GET'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def analysis_dashboard(request):
    try:
        dashboard_user = request.user.dashboard_obj
        emp_id = dashboard_user.emp_id
        industry = dashboard_user.industry

        line_number = dashboard_user.line_number
        department = dashboard_user.department
        account_created_time = dashboard_user.created_at
        total_annotated_images = Annotation.objects.filter(user=dashboard_user, industry=industry).values('image_id').distinct().count()

        detections = DetectionResult.objects.filter(emp_id=emp_id, industry=industry)

        selected_date = request.query_params.get('date')
        if selected_date:
            parsed_date = parse_date(selected_date)
            if parsed_date is None:
                return Response(ErrorResponseSerializer({'error': 'Invalid date format. Use YYYY-MM-DD.'}).data, status=status.HTTP_400_BAD_REQUEST)
            detections = detections.filter(created_at__date=parsed_date)

        defects_found = []
        dates = detections.values_list('created_at__date', flat=True).distinct()
        for date in dates:
            date_detections = detections.filter(created_at__date=date)
            detections_list = []
            for d in date_detections:
                detections_list.append({
                    'time': d.created_at.strftime('%H:%M:%S'),
                    'defect_result': d.defect_result,
                    'source': d.source,
                    'industry': d.industry
                })
            defects_found.append({
                'date': date.strftime('%Y-%m-%d'),
                'detections': detections_list
            })

        return Response({
            'line_number': line_number,
            'department': department,
            'industry': industry,
            'account_created_time': account_created_time,
            'total_annotated_images': total_annotated_images,
            'defects_found': defects_found
        }, status=status.HTTP_200_OK)

    except AttributeError:
        logger.error(f"Authentication error: User data not found")
        return Response(ErrorResponseSerializer({'error': 'User authentication data not found'}).data, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Error fetching analysis data: {str(e)}")
        return Response(ErrorResponseSerializer({'error': str(e)}).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################## Total Annotated Images API ####################
@swagger_auto_schema(
    method='get',
    operation_summary="Get total annotated images for the authenticated user",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
    ],
    responses={
        200: openapi.Response(
            description="Total annotated images",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'total_annotated_images': openapi.Schema(type=openapi.TYPE_INTEGER),
                    'industry': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        401: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['GET'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def total_annotated_images(request):
    try:
        dashboard_user = request.user.dashboard_obj
        industry = dashboard_user.industry
        total = Annotation.objects.filter(user=dashboard_user, industry=industry).values('image_id').distinct().count()
        return Response({
            'total_annotated_images': total,
            'industry': industry
        }, status=status.HTTP_200_OK)
    except AttributeError:
        return Response(ErrorResponseSerializer({'error': 'User authentication data not found'}).data, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Error fetching annotated images count: {str(e)}")
        return Response(ErrorResponseSerializer({'error': str(e)}).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################## Defects by Date API ####################
@swagger_auto_schema(
    method='get',
    operation_summary="Get defects found by date for the authenticated user",
    manual_parameters=[
        openapi.Parameter('date', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, description='Optional date filter (YYYY-MM-DD)'),
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
    ],
    responses={
        200: openapi.Response(
            description="Defects found by date",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'date': openapi.Schema(type=openapi.TYPE_STRING, format='date'),
                        'detections': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'time': openapi.Schema(type=openapi.TYPE_STRING, format='time'),
                                    'defect_result': openapi.Schema(type=openapi.TYPE_STRING),
                                    'source': openapi.Schema(type=openapi.TYPE_STRING),
                                    'industry': openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            )
                        )
                    }
                )
            )
        ),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['GET'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def defects_by_date(request):
    try:
        dashboard_user = request.user.dashboard_obj
        emp_id = dashboard_user.emp_id
        industry = dashboard_user.industry

        detections = DetectionResult.objects.filter(emp_id=emp_id, industry=industry)

        selected_date = request.query_params.get('date')
        if selected_date:
            parsed_date = parse_date(selected_date)
            if parsed_date is None:
                return Response(ErrorResponseSerializer({'error': 'Invalid date format. Use YYYY-MM-DD.'}).data, status=status.HTTP_400_BAD_REQUEST)
            detections = detections.filter(created_at__date=parsed_date)

        defects_found = []
        dates = detections.values_list('created_at__date', flat=True).distinct()
        for date in dates:
            date_detections = detections.filter(created_at__date=date)
            detections_list = []
            for d in date_detections:
                detections_list.append({
                    'time': d.created_at.strftime('%H:%M:%S'),
                    'defect_result': d.defect_result,
                    'source': d.source,
                    'industry': d.industry
                })
            defects_found.append({
                'date': date.strftime('%Y-%m-%d'),
                'detections': detections_list
            })

        return Response(defects_found, status=status.HTTP_200_OK)
    except AttributeError:
        return Response(ErrorResponseSerializer({'error': 'User authentication data not found'}).data, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Error fetching defects by date: {str(e)}")
        return Response(ErrorResponseSerializer({'error': str(e)}).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################## Login Details API ####################
@swagger_auto_schema(
    method='get',
    operation_summary="Get login details for the authenticated user",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
    ],
    responses={
        200: openapi.Response(
            description="Login details",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'line_number': openapi.Schema(type=openapi.TYPE_STRING),
                    'department': openapi.Schema(type=openapi.TYPE_STRING),
                    'industry': openapi.Schema(type=openapi.TYPE_STRING),
                    'created_time': openapi.Schema(type=openapi.TYPE_STRING, format='date-time')
                }
            )
        ),
        401: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['GET'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def login_details(request):
    try:
        dashboard_user = request.user.dashboard_obj
        return Response({
            'line_number': dashboard_user.line_number,
            'department': dashboard_user.department,
            'industry': dashboard_user.industry,
            'created_time': dashboard_user.created_at
        }, status=status.HTTP_200_OK)
    except AttributeError:
        return Response(ErrorResponseSerializer({'error': 'User authentication data not found'}).data, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Error fetching login details: {str(e)}")
        return Response(ErrorResponseSerializer({'error': str(e)}).data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

################## Admin List Users API ####################
@swagger_auto_schema(
    method='get',
    operation_summary="List all users (Admin only)",
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token'
        ),
    ],
    responses={
        200: UserSerializer(many=True),
        403: ErrorResponseSerializer,
        401: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['GET'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def admin_list_users(request):
    if not request.user.is_admin:
        return Response(ErrorResponseSerializer({'error': 'Admin access required'}).data, status=status.HTTP_403_FORBIDDEN)
    
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

################## Admin User Detail API ####################
@swagger_auto_schema(
    method='get',
    operation_summary="Get user details (Admin only)",
    manual_parameters=[
        openapi.Parameter(
            name='emp_id',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            required=True,
            description='Employee ID'
        ),
        openapi.Parameter(
            name='date',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description='Date for detections (YYYY-MM-DD, default today)'
        ),
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token'
        ),
    ],
    responses={
        200: openapi.Response(
            description="User details",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'annotations_total': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'detections_today': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'defect_types_today': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(type=openapi.TYPE_INTEGER),
                            description="Dictionary of defect class names and their counts"
                        ),
                        'logins_total': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'industry': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        ),
        400: ErrorResponseSerializer,
        403: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
        404: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['GET'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def admin_user_detail(request, emp_id):
    if not request.user.is_admin:
        return Response(ErrorResponseSerializer({'error': 'Admin access required'}).data, status=status.HTTP_403_FORBIDDEN)
    
    dashboard_user = Dashboard.objects.filter(emp_id=emp_id).first()
    if not dashboard_user:
        return Response(ErrorResponseSerializer({'error': 'User not found'}).data, status=status.HTTP_404_NOT_FOUND)
    
    industry = dashboard_user.industry
    annotations_total = Annotation.objects.filter(user=dashboard_user, industry=industry).count()
    
    date_str = request.GET.get('date')
    if date_str:
        date_obj = parse_date(date_str)
        if not date_obj:
            return Response(ErrorResponseSerializer({'error': 'Invalid date format'}).data, status=status.HTTP_400_BAD_REQUEST)
    else:
        date_obj = datetime.date.today()
    
    detections = DetectionResult.objects.filter(emp_id=emp_id, created_at__date=date_obj, industry=industry)
    detections_today = detections.count()
    
    defect_counter = Counter()
    for detection in detections:
        defect_result = detection.defect_result or []
        if isinstance(defect_result, str):
            try:
                defect_result = json.loads(defect_result)
            except json.JSONDecodeError:
                continue
        if not isinstance(defect_result, list):
            continue
        for defect in defect_result:
            if isinstance(defect, dict):
                class_name = defect.get('class')
                if class_name:
                    defect_counter[class_name] += 1
    
    logins_total = LoginHistory.objects.filter(user=dashboard_user).count()
    
    return Response([{
        'annotations_total': annotations_total,
        'detections_today': detections_today,
        'defect_types_today': defect_counter,
        'logins_total': logins_total,
        'industry': industry
    }], status=status.HTTP_200_OK)

################## Admin All Users Detail API ####################
@swagger_auto_schema(
    method='get',
    operation_summary="Get details for all users (Admin only)",
    manual_parameters=[
        openapi.Parameter(
            name='date',
            in_=openapi.IN_QUERY,
            type=openapi.TYPE_STRING,
            required=False,
            description='Date for detections (YYYY-MM-DD, default today)'
        ),
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token'
        ),
    ],
    responses={
        200: openapi.Response(
            description="Details for all users",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'EMP_ID': openapi.Schema(type=openapi.TYPE_STRING),
                        'annotations_total': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'detections_today': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'defect_types_today': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(type=openapi.TYPE_INTEGER),
                            description='Dictionary of defect class names and their counts for the specified date'
                        ),
                        'logins_total': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'industry': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        ),
        400: ErrorResponseSerializer,
        403: ErrorResponseSerializer,
        401: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['GET'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def admin_all_users_detail(request):
    if not request.user.is_admin:
        return Response(ErrorResponseSerializer({'error': 'Admin access required'}).data, status=status.HTTP_403_FORBIDDEN)
    
    date_str = request.GET.get('date')
    if date_str:
        date_obj = parse_date(date_str)
        if not date_obj:
            return Response(ErrorResponseSerializer({'error': 'Invalid date format'}).data, status=status.HTTP_400_BAD_REQUEST)
    else:
        date_obj = datetime.date.today()
    
    emp_ids = DetectionResult.objects.values('emp_id').distinct()
    
    users_data = []
    for emp in emp_ids:
        emp_id = emp['emp_id']
        dashboard_user = Dashboard.objects.filter(emp_id=emp_id).first()
        
        industry = dashboard_user.industry if dashboard_user else None
        annotations_total = Annotation.objects.filter(user=dashboard_user, industry=industry).count() if dashboard_user else 0
        
        detections = DetectionResult.objects.filter(emp_id=emp_id, created_at__date=date_obj, industry=industry)
        detections_today = detections.count()
        
        defect_types = {}
        for detection in detections:
            defect_result = detection.defect_result or []
            if isinstance(defect_result, str):
                try:
                    defect_result = json.loads(defect_result)
                except json.JSONDecodeError:
                    continue
            if not isinstance(defect_result, list):
                continue
            for defect in defect_result:
                if not isinstance(defect, dict):
                    continue
                class_name = defect.get('class')
                if class_name:
                    defect_types[class_name] = defect_types.get(class_name, 0) + 1
        
        logins_total = LoginHistory.objects.filter(user=dashboard_user).count() if dashboard_user else 0
        
        users_data.append({
            'EMP_ID': emp_id,
            'annotations_total': annotations_total,
            'detections_today': detections_today,
            'defect_types_today': defect_types,
            'logins_total': logins_total,
            'industry': industry
        })
    
    return Response(users_data, status=status.HTTP_200_OK)

################## Admin Delete User API ####################
@swagger_auto_schema(
    method='delete',
    operation_summary="Delete a user (Admin only)",
    manual_parameters=[
        openapi.Parameter(
            name='emp_id',
            in_=openapi.IN_PATH,
            type=openapi.TYPE_STRING,
            required=True,
            description='Employee ID'
        ),
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token'
        ),
    ],
    responses={
        204: "User deleted",
        403: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
        404: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['DELETE'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def admin_delete_user(request, emp_id):
    if not request.user.is_admin:
        return Response(ErrorResponseSerializer({'error': 'Admin access required'}).data, status=status.HTTP_403_FORBIDDEN)
    
    dashboard_user = Dashboard.objects.filter(emp_id=emp_id).first()
    if not dashboard_user:
        return Response(ErrorResponseSerializer({'error': 'User not found'}).data, status=status.HTTP_404_NOT_FOUND)
    
    User.objects.filter(emp_id=emp_id).delete()
    dashboard_user.delete()
    
    return Response(status=status.HTTP_204_NO_CONTENT)




#################### NEW API: Get Industries List #####################

@swagger_auto_schema(
    method='get',
    operation_summary="Get list of industries",
    responses={
        200: openapi.Response(
            description="List of industries",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'industries': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_STRING)
                    )
                }
            )
        )
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_industries_list(request):
    return Response({"industries": industries})


#################### NEW API: Set User Industry #####################

@swagger_auto_schema(
    method='post',
    operation_summary="Set user's industry",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['industry'],
        properties={
            'industry': openapi.Schema(type=openapi.TYPE_STRING)
        }
    ),
    responses={
        200: "success",
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['POST'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def set_user_industry(request):
    industry = request.data.get('industry')
    if not industry:
        return Response(ErrorResponseSerializer({'error': 'industry is required'}), status=status.HTTP_400_BAD_REQUEST)
    if industry not in industries:
        return Response(ErrorResponseSerializer({'error': 'Invalid industry'}), status=status.HTTP_400_BAD_REQUEST)
    try:
        dashboard_user = request.user.dashboard_obj
        dashboard_user.industry = industry  # Assuming 'industry' field exists in Dashboard model
        dashboard_user.save()
        return Response({'message': 'Industry updated successfully'}, status=status.HTTP_200_OK)
    except AttributeError:
        return Response(ErrorResponseSerializer({'error': 'User authentication data not found'}), status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Error setting industry: {str(e)}")
        return Response(ErrorResponseSerializer({'error': str(e)}), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#################### NEW API: Consolidate and Train #####################


@swagger_auto_schema(
    method='post',
    operation_summary="Consolidate sessions and train model for industry",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['industry', 'epochs'],
        properties={
            'industry': openapi.Schema(type=openapi.TYPE_STRING),
            'epochs': openapi.Schema(type=openapi.TYPE_INTEGER),
            'from_scratch': openapi.Schema(type=openapi.TYPE_BOOLEAN, default=True)
        }
    ),
    manual_parameters=[
        openapi.Parameter(
            name='Authorization',
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            required=True,
            description='Bearer token in the format: Bearer <token>'
        ),
    ],
    responses={
        200: openapi.Response(
            description="Training started or completed",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'model_path': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        ),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer,
        403: ErrorResponseSerializer,
        500: ErrorResponseSerializer
    },
    security=[{'BearerAuth': []}]
)
@api_view(['POST'])
@authentication_classes([DashboardJWTAuthentication])
@permission_classes([IsAuthenticated])
def consolidate_and_train(request):
    if not request.user.is_admin:
        serializer = ErrorResponseSerializer({'error': 'Admin access required'})
        logger.error(f"Non-admin user attempted to access consolidate_and_train: {request.user}")
        return Response(serializer.data, status=status.HTTP_403_FORBIDDEN)

    industry = request.data.get('industry')
    if not industry:
        serializer = ErrorResponseSerializer({'error': 'industry is required'})
        logger.error("Missing industry in request data")
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    try:
        epochs = int(request.data['epochs'])
        if epochs <= 0:
            raise ValueError("epochs must be a positive integer")
    except (KeyError, ValueError, TypeError) as e:
        serializer = ErrorResponseSerializer({'error': f'valid epochs required: {str(e)}'})
        logger.error(f"Invalid epochs value: {request.data.get('epochs')}, error: {str(e)}")
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    from_scratch = request.data.get('from_scratch', True)
    logger.info(f"Starting consolidation and training for industry: {industry}, epochs: {epochs}, from_scratch: {from_scratch}")

    # Get yaml_paths from redis
    key = f"industry_yaml:{industry}"
    yaml_paths = redis_client.lrange(key, 0, -1)
    if not yaml_paths:
        serializer = ErrorResponseSerializer({'error': 'No sessions found for this industry'})
        logger.error(f"No YAML paths found for industry: {industry}")
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Consolidate
        all_classes = set()
        session_data = []
        for yaml_p in yaml_paths:
            logger.debug(f"Processing YAML path: {yaml_p}")
            if not os.path.exists(yaml_p):
                logger.warning(f"YAML file not found: {yaml_p}")
                continue
            try:
                with open(yaml_p, 'r') as f:
                    yaml_data = yaml.safe_load(f)
                    if not all(key in yaml_data for key in ['path', 'train', 'val', 'names']):
                        logger.warning(f"Invalid YAML structure in {yaml_p}")
                        continue
                    session_data.append({
                        'path': yaml_data['path'],
                        'train': yaml_data['train'],
                        'val': yaml_data['val'],
                        'names': yaml_data['names']
                    })
                    for name in yaml_data['names'].values():
                        all_classes.add(name)
            except Exception as e:
                logger.warning(f"Failed to process YAML file {yaml_p}: {str(e)}")
                continue

        if not session_data:
            serializer = ErrorResponseSerializer({'error': 'No valid sessions found for this industry'})
            logger.error(f"No valid session data for industry: {industry}")
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

        unique_classes = sorted(all_classes)
        new_class_to_id = {name: idx for idx, name in enumerate(unique_classes)}
        logger.info(f"Consolidated {len(unique_classes)} unique classes: {unique_classes}")

        # Create consolidated folder
        consol_folder = os.path.normpath(os.path.join(settings.BASE_DIR, 'yolo_datasets', industry, f'consolidated_{str(uuid.uuid4())}')).replace('\\', '/')
        os.makedirs(consol_folder, exist_ok=True)
        train_images_dir = os.path.normpath(os.path.join(consol_folder, 'images', 'train')).replace('\\', '/')
        train_labels_dir = os.path.normpath(os.path.join(consol_folder, 'labels', 'train')).replace('\\', '/')
        os.makedirs(train_images_dir, exist_ok=True)
        os.makedirs(train_labels_dir, exist_ok=True)

        for sess in session_data:
            old_images_dir = os.path.normpath(os.path.join(sess['path'], sess['train'])).replace('\\', '/')
            old_labels_dir = os.path.normpath(os.path.join(sess['path'], 'labels', 'train')).replace('\\', '/')
            old_id_to_name = sess['names']

            if not os.path.exists(old_images_dir) or not os.path.exists(old_labels_dir):
                logger.warning(f"Image or label directory not found: {old_images_dir}, {old_labels_dir}")
                continue

            try:
                for img_file in os.listdir(old_images_dir):
                    if not img_file.endswith('.jpg'):
                        continue
                    base = os.path.splitext(img_file)[0]
                    old_img_p = os.path.normpath(os.path.join(old_images_dir, img_file)).replace('\\', '/')
                    old_lab_p = os.path.normpath(os.path.join(old_labels_dir, f"{base}.txt")).replace('\\', '/')
                    if not os.path.exists(old_lab_p):
                        logger.warning(f"Label file not found: {old_lab_p}")
                        continue
                    new_base = str(uuid.uuid4())
                    new_img_p = os.path.normpath(os.path.join(train_images_dir, f"{new_base}.jpg")).replace('\\', '/')
                    new_lab_p = os.path.normpath(os.path.join(train_labels_dir, f"{new_base}.txt")).replace('\\', '/')
                    try:
                        shutil.copyfile(old_img_p, new_img_p)
                        with open(old_lab_p, 'r') as f:
                            lines = f.readlines()
                        with open(new_lab_p, 'w') as f:
                            for line in lines:
                                parts = line.strip().split()
                                try:
                                    old_class_id = int(parts[0])
                                    old_name = old_id_to_name.get(old_class_id)
                                    if old_name is None:
                                        logger.warning(f"Invalid class ID {old_class_id} in {old_lab_p}")
                                        continue
                                    new_class_id = new_class_to_id[old_name]
                                    parts[0] = str(new_class_id)
                                    f.write(' '.join(parts) + '\n')
                                except (KeyError, ValueError) as e:
                                    logger.warning(f"Error remapping class for {old_lab_p}: {str(e)}")
                                    continue
                    except Exception as e:
                        logger.error(f"Error processing image/label {old_img_p}: {str(e)}")
                        continue
            except Exception as e:
                logger.error(f"Error processing session data for {old_images_dir}: {str(e)}")
                continue

        # Verify that images and labels were copied
        if not os.listdir(train_images_dir) or not os.listdir(train_labels_dir):
            serializer = ErrorResponseSerializer({'error': 'No valid images or labels found for training'})
            logger.error(f"No valid images or labels in {train_images_dir} or {train_labels_dir}")
            return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)

        # Create consolidated YAML
        consol_yaml = os.path.normpath(os.path.join(consol_folder, 'data.yaml')).replace('\\', '/')
        try:
            with open(consol_yaml, 'w') as f:
                f.write(f"path: {consol_folder}\ntrain: images/train\nval: images/train\nnc: {len(unique_classes)}\nnames:\n")
                for idx, name in enumerate(unique_classes):
                    f.write(f"  {idx}: {name}\n")
            logger.info(f"Created consolidated YAML: {consol_yaml}")
        except Exception as e:
            logger.error(f"Failed to create YAML file {consol_yaml}: {str(e)}")
            serializer = ErrorResponseSerializer({'error': f'Failed to create YAML file: {str(e)}'})
            return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Train
        try:
            if from_scratch:
                train_model = YOLO('yolov8n.yaml')
            else:
                train_model = YOLO('yolov8n.pt')
            train_model.train(data=consol_yaml, epochs=epochs, project='runs', name=industry)
            logger.info(f"Training completed for industry: {industry}")
        except Exception as e:
            logger.error(f"Training failed for industry {industry}: {str(e)}")
            serializer = ErrorResponseSerializer({'error': f'Training failed: {str(e)}'})
            return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Copy trained model
        trained_path = os.path.join('runs', industry, 'weights', 'best.pt')
        final_path = os.path.join(settings.BASE_DIR, f"{industry}_model.pt")
        if os.path.exists(trained_path):
            try:
                shutil.copy(trained_path, final_path)
                logger.info(f"Model copied to: {final_path}")
            except Exception as e:
                logger.error(f"Failed to copy model from {trained_path} to {final_path}: {str(e)}")
                serializer = ErrorResponseSerializer({'error': f'Failed to copy trained model: {str(e)}'})
                return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.error(f"Trained model not found at: {trained_path}")
            serializer = ErrorResponseSerializer({'error': 'Trained model not found'})
            return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Clear the Redis list
        try:
            redis_client.delete(key)
            logger.info(f"Cleared Redis key: {key}")
        except Exception as e:
            logger.error(f"Failed to clear Redis key {key}: {str(e)}")
            # Continue despite Redis deletion failure, as training is complete

        return Response({'message': 'Training completed', 'model_path': final_path}, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Unexpected error in consolidate_and_train for industry {industry}: {str(e)}")
        serializer = ErrorResponseSerializer({'error': f'Server error: {str(e)}'})
        return Response(serializer.data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)