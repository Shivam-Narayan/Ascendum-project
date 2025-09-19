# from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from transformers import AutoImageProcessor, AutoModelForImageClassification
from ultralytics import YOLO
import os, cv2, uuid, logging, joblib
from sklearn.cluster import KMeans
import numpy as np
from PIL import Image
from .serializers import RegisterSerializer, LoginSerializer, ErrorResponseSerializer, UserActivitySerializer
from .models import UserActivity
from .swagger import REGISTER_SWAGGER, LOGIN_SWAGGER, PREDICT_SWAGGER, Activity_Log_SWAGGER
from django.utils.dateparse import parse_date
from rest_framework.pagination import PageNumberPagination
from PIL import Image, ImageDraw
from django.conf import settings




# Set up logging
logger = logging.getLogger(__name__)

# Define model paths separately
MODEL_PATHS = {
    'Plant disease': {
        'processor': 'A2H0H0R1/swin-tiny-patch4-window7-224-plant-disease-new',
        'model': 'A2H0H0R1/swin-tiny-patch4-window7-224-plant-disease-new'
    },
    'Cotton Pests': {
        'processor': 'RohithN2004/Cotton-pests',
        'model': 'RohithN2004/Cotton-pests'
    },
    'Tomato': {
        'model': r'C:\Users\pathalamm\Desktop\Agrovet_be\Ascendum_demo\agrovet_be\models\Tomato.pt'
    },
    'Banana': {
        'model': r'C:\Users\pathalamm\Desktop\Agrovet_be\Ascendum_demo\agrovet_be\models\Banana.pt'
    },
    'mango': { 
        'model': r'C:\Users\pathalamm\Desktop\Agrovet_be\Ascendum_demo\agrovet_be\models\mango.pt'
    },
    'Soil Nutrition': {
        'regressor': r'C:\Users\pathalamm\Desktop\Agrovet_be\Ascendum_demo\agrovet_be\models\best_regressor_model.pkl',
        'classifier': r'C:\Users\pathalamm\Desktop\Agrovet_be\Ascendum_demo\agrovet_be\models\best_classifier_model.pkl',
        'label_encoder': r'C:\Users\pathalamm\Desktop\Agrovet_be\Ascendum_demo\agrovet_be\models\label_encoder.pkl'
    }
}



def load_model(model_name):
    """Load the specified model and processor based on model_name."""
    try:
        if model_name not in MODEL_PATHS:
            raise ValueError(f"Unknown model: {model_name}")

        config = MODEL_PATHS[model_name]
        if model_name in ["Plant disease", "Cotton Pests"]:
            processor = AutoImageProcessor.from_pretrained(config['processor'])
            model = AutoModelForImageClassification.from_pretrained(config['model'])
            logger.info(f"Loaded model: {model_name} from Hugging Face ({config['model']})")
            return processor, model
        elif model_name in ["Tomato", "Banana", "mango"]:
            model_path = config['model']
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            model = YOLO(model_path)
            logger.info(f"Loaded model: {model_name} from {model_path}")
            return None, model
        elif model_name == "Soil Nutrition":
            regressor_path = config['regressor']
            classifier_path = config['classifier']
            le_path = config['label_encoder']
            for path in [regressor_path, classifier_path, le_path]:
                if not os.path.exists(path):
                    raise FileNotFoundError(f"Model file not found: {path}")
            best_regressor_model = joblib.load(regressor_path)
            best_classifier_model = joblib.load(classifier_path)
            le = joblib.load(le_path)
            model = (best_regressor_model, best_classifier_model, le)
            logger.info(f"Loaded model: {model_name} from {regressor_path}, {classifier_path}, {le_path}")
            return None, model
    except FileNotFoundError as e:
        logger.error(f"FileNotFoundError: {str(e)}")
        raise ValueError(f"Failed to load model: {str(e)}")
    except Exception as e:
        logger.error(f"Error loading model {model_name}: {str(e)}")
        raise ValueError(f"Failed to load model: {str(e)}")



####################################### Register API #######################################


@swagger_auto_schema(**REGISTER_SWAGGER)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user and return a JWT access token."""
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        # access_token = AccessToken.for_user(user)
        # Log registration activity
        UserActivity.objects.create(
            user=user,
            activity_type='registration',
            details={'message': 'User registered'}
        )
        return Response({
            "message": "User registered successfully",
            # "data": {
            #     "access": str(access_token),
            #     # "email": user.email,
            #     # "name": getattr(user, 'name', user.username)
            # }
        }, status=status.HTTP_201_CREATED)
    return Response(
        ErrorResponseSerializer({'error': serializer.errors}).data,
        status=status.HTTP_400_BAD_REQUEST
    )




####################################### Login API #######################################


@swagger_auto_schema(**LOGIN_SWAGGER)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Authenticate a user or admin and return a JWT access token."""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            ErrorResponseSerializer({'error': serializer.errors}).data,
            status=status.HTTP_400_BAD_REQUEST
        )
    user = serializer.validated_data.get("user")
    is_admin = serializer.validated_data.get("is_admin", False)
    if not user:
        return Response(
            ErrorResponseSerializer({'error': 'Invalid credentials'}).data,
            status=status.HTTP_401_UNAUTHORIZED
        )
    access_token = AccessToken.for_user(user)
    # Log login activity
    UserActivity.objects.create(
        user=user,
        activity_type='login',
        details={'message': 'User logged in', 'is_admin': is_admin}
    )
    return Response({
        "message": "Login successful",
        "token": str(access_token),
        # "user": {
        #     "email": user.email,
        #     "name": getattr(user, 'name', user.username),
        #     "is_admin": is_admin
        # }
    }, status=status.HTTP_200_OK)



####################################### Activity Log API #######################################


@swagger_auto_schema(**Activity_Log_SWAGGER)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_log(request):
    user = request.user
    user_id = request.query_params.get('user_id')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    group_by_day = request.query_params.get('group_by_day', 'false').lower() == 'true'

    if user.is_admin:
        activities = UserActivity.objects.filter(activity_type__in=['login', 'prediction'])
        if user_id:
            activities = activities.filter(user_id=user_id)
    else:
        activities = UserActivity.objects.filter(user=user, activity_type__in=['login', 'prediction'])

    if start_date:
        start_date_obj = parse_date(start_date)
        if start_date_obj:
            activities = activities.filter(timestamp__date__gte=start_date_obj)
    if end_date:
        end_date_obj = parse_date(end_date)
        if end_date_obj:
            activities = activities.filter(timestamp__date__lte=end_date_obj)

    activities = activities.order_by('-timestamp')

    if group_by_day:
        from collections import defaultdict
        grouped = defaultdict(list)
        for activity in activities:
            day_str = activity.timestamp.date().isoformat()
            grouped[day_str].append(UserActivitySerializer(activity).data)

        result = [{'date': date, 'activities': acts} for date, acts in sorted(grouped.items(), reverse=True)]
        return Response(result, status=status.HTTP_200_OK)

    # Manual Pagination Setup
    paginator = PageNumberPagination()
    paginator.page_size = 10
    paginated_qs = paginator.paginate_queryset(activities, request)

    serialized = UserActivitySerializer(paginated_qs, many=True)
    return paginator.get_paginated_response(serialized.data)




####################################### Predict API #######################################



@swagger_auto_schema(**PREDICT_SWAGGER)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def predict(request):
    """Handle prediction requests for the specified model."""
    model_name = request.query_params.get('model_name')
    if not model_name:
        return Response(
            ErrorResponseSerializer({'error': "model_name is required"}).data,
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        processor, model = load_model(model_name)
    except ValueError as e:
        return Response(
            ErrorResponseSerializer({'error': str(e)}).data,
            status=status.HTTP_400_BAD_REQUEST
        )

    if 'image' not in request.FILES:
        return Response(
            ErrorResponseSerializer({'error': "At least one image file is required"}).data,
            status=status.HTTP_400_BAD_REQUEST
        )

    images = request.FILES.getlist('image')
    results_list = []

    for image_file in images:
        try:
            image = Image.open(image_file).convert('RGB')

            # ===== Plant disease / Cotton Pests =====
            if model_name in ["Plant disease", "Cotton Pests"]:
                inputs = processor(images=image, return_tensors="pt")
                outputs = model(**inputs)
                probabilities = outputs.logits.softmax(dim=-1)
                predicted_class = probabilities.argmax().item()
                confidence = probabilities[0][predicted_class].item()

                results_list.append({
                    "predicted_class": model.config.id2label[predicted_class],
                    "confidence": confidence
                })

            # ===== Tomato / Banana / Mango =====
            elif model_name in ["Tomato", "Banana", "mango"]:
                results = model(image)  # YOLO model inference

                draw = ImageDraw.Draw(image)
                predictions = []
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        cls_id = int(box.cls)
                        confidence = float(box.conf)
                        bbox = box.xyxy.tolist()[0]
                        class_name = result.names[cls_id]

                        draw.rectangle(bbox, outline='red', width=3)
                        draw.text((bbox[0], bbox[1] - 10), f"{class_name}: {confidence:.2f}", fill='red')

                        predictions.append({
                            "class": class_name,
                            "confidence": confidence,
                            # "bbox": bbox
                        })

                # Save annotated image
                save_dir = os.path.join(settings.MEDIA_ROOT, 'predictions')
                os.makedirs(save_dir, exist_ok=True)
                unique_filename = f"{uuid.uuid4()}.jpg"
                save_path = os.path.join(save_dir, unique_filename)
                image.save(save_path)

                image_url = request.build_absolute_uri(settings.MEDIA_URL + f'predictions/{unique_filename}')

                results_list.append({
                    "predictions": predictions,
                    "image_with_bboxes_url": image_url
                })

            # ===== Soil Nutrition =====
            elif model_name == "Soil Nutrition":
                image_np = np.array(image)
                image_bgr = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
                smoothed_image = cv2.GaussianBlur(image_bgr, (5, 5), 0)
                reshaped_image = smoothed_image.reshape((-1, 3))
                kmeans = KMeans(n_clusters=3, random_state=0).fit(reshaped_image)
                dominant_color = kmeans.cluster_centers_[0]

                best_regressor_model, best_classifier_model, le = model
                regression_pred = best_regressor_model.predict([dominant_color])[0]
                classifier_pred_proba = best_classifier_model.predict_proba([dominant_color])[0]
                classifier_pred = np.argmax(classifier_pred_proba)
                class_label = le.inverse_transform([classifier_pred])[0]
                confidence = classifier_pred_proba[classifier_pred]

                results_list.append({
                    "regression_prediction": float(regression_pred),
                    "classifier_prediction": class_label,
                    "confidence": float(confidence)
                })

        except Exception as e:
            results_list.append({
                "error": f"Failed to process image '{image_file.name}': {str(e)}"
            })

    # Log prediction activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='prediction',
        details={
            'model': model_name,
            'results': results_list
        }
    )

    return Response({"results": results_list}, status=status.HTTP_200_OK)

