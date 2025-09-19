from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from .serializers import RegisterSerializer, LoginSerializer, ErrorResponseSerializer, UserDetailSerializer

# Swagger schema for register API
REGISTER_SWAGGER = {
    'method': 'post',
    'request_body': RegisterSerializer,
    'responses': {
        201: openapi.Response(
            description="User registered successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="User registered successfully"),
                    'data': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'access': openapi.Schema(type=openapi.TYPE_STRING, description='JWT access token'),
                            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            )
        ),
        400: ErrorResponseSerializer
    }
}

# Swagger schema for login API
LOGIN_SWAGGER = {
    'method': 'post',
    'request_body': LoginSerializer,
    'responses': {
        200: openapi.Response(
            description="Login successful",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, example="Login successful"),
                    'token': openapi.Schema(type=openapi.TYPE_STRING, description="JWT token"),
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'is_admin': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        }
                    )
                }
            )
        ),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer
    }
}

# Swagger schema for predict API


PREDICT_SWAGGER = {
    'method': 'post',
    'operation_description': (
        "Predict using selected model. Requires JWT token from /api/login/ "
        "in Authorization header (Bearer <token>)."
    ),
    'request_body': None,
    'manual_parameters': [
        openapi.Parameter(
            'model_name', openapi.IN_QUERY,
            description=(
                "Model to use for prediction. Must be one of: Plant disease, Cotton Pests, "
                "Tomato, Banana, mango, Soil Nutrition"
            ),
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'image', openapi.IN_FORM,
            description=(
                "Image file for prediction (required for Plant disease, Cotton Pests, "
                "Tomato, Banana, mango models)"
            ),
            type=openapi.TYPE_FILE,
            required=False
        ),
        openapi.Parameter(
            'Authorization', openapi.IN_HEADER,
            description="JWT token (Bearer <token>) obtained from /api/login/ or /api/token/",
            type=openapi.TYPE_STRING,
            required=True
        )
    ],
    'responses': {
        200: openapi.Response(
            description="Prediction results",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'predicted_class': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Predicted class for image models (Plant disease, Cotton Pests)"
                    ),
                    'confidence': openapi.Schema(
                        type=openapi.TYPE_NUMBER,
                        description="Confidence score for image models"
                    ),
                    'predictions': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        description="List of predictions for YOLO models (Tomato, Banana, mango)",
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'class': openapi.Schema(type=openapi.TYPE_STRING),
                                'confidence': openapi.Schema(type=openapi.TYPE_NUMBER),
                                'bbox': openapi.Schema(
                                    type=openapi.TYPE_ARRAY,
                                    description="Bounding box coordinates [x1, y1, x2, y2]",
                                    items=openapi.Schema(type=openapi.TYPE_NUMBER)
                                )
                            }
                        )
                    ),
                    'image_with_bboxes_url': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="URL of the image with bounding boxes for YOLO models"
                    ),
                    'regression_prediction': openapi.Schema(
                        type=openapi.TYPE_NUMBER,
                        description="Regression output for Soil Nutrition"
                    ),
                    'classifier_prediction': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        description="Classifier output for Soil Nutrition"
                    )
                }
            )
        ),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer
    }
}


# Swagger schema for users API
Activity_Log_SWAGGER = {
    'method': 'get',
    'operation_description': (
        "Retrieve login and prediction activities only. "
        "Admin users can view activities of all users, while regular users can view only their own activities. "
        "Requires JWT token in Authorization header (Bearer <token>)."
    ),
    'manual_parameters': [
        openapi.Parameter(
            'Authorization', openapi.IN_HEADER,
            description="JWT token (Bearer <token>) obtained from /api/login/",
            type=openapi.TYPE_STRING,
            required=True
        ),
        openapi.Parameter(
            'user_id', openapi.IN_QUERY,
            description="Optional: Filter activities by specific user ID (admin only)",
            type=openapi.TYPE_INTEGER,
            required=False
        ),
        openapi.Parameter(
            'start_date', openapi.IN_QUERY,
            description="Optional: Filter activities from this start date (format: YYYY-MM-DD)",
            type=openapi.FORMAT_DATE,
            required=False
        ),
        openapi.Parameter(
            'end_date', openapi.IN_QUERY,
            description="Optional: Filter activities up to this end date (format: YYYY-MM-DD)",
            type=openapi.FORMAT_DATE,
            required=False
        ),
        openapi.Parameter(
            'group_by_day', openapi.IN_QUERY,
            description="Optional: Set to 'true' to group activities by day (default is false)",
            type=openapi.TYPE_BOOLEAN,
            required=False
        )
    ],
    'responses': {
        200: openapi.Response(
            description="List of login and prediction activities",
            schema=openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                'email': openapi.Schema(type=openapi.TYPE_STRING, format='email', example="user@example.com"),
                                'name': openapi.Schema(type=openapi.TYPE_STRING, example="John Doe"),
                                'username': openapi.Schema(type=openapi.TYPE_STRING, example="johndoe"),
                                'is_admin': openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                            }
                        ),
                        'activities': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'activity_type': openapi.Schema(type=openapi.TYPE_STRING, example="prediction"),
                                    'details': openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        example={"predicted_class": "disease", "confidence": 0.95}
                                    ),
                                    'timestamp': openapi.Schema(
                                        type=openapi.TYPE_STRING, format='date-time',
                                        example="2025-09-08T12:00:00Z"
                                    ),
                                }
                            )
                        )
                    }
                )
            )
        ),
        401: openapi.Response(
            description="Authentication credentials were not provided or invalid.",
            schema=ErrorResponseSerializer
        ),
        403: openapi.Response(
            description="Admin access required",
            schema=ErrorResponseSerializer
        )
    }
}

# Swagger UI view
schema_view = get_schema_view(
    openapi.Info(
        title="Agrovet API",
        default_version='v1',
        description="API for user authentication, model predictions, and user activity management",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=False,
    permission_classes=[permissions.IsAuthenticated],
)