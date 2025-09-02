from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import RegisterSerializer, LoginSerializer, ErrorResponseSerializer


################## Register API ####################

@swagger_auto_schema(
    method='post',
    request_body=RegisterSerializer,
    responses={
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
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        access_token = AccessToken.for_user(user)
        return Response({
            "message": "User registered successfully",
            "data": {
                "access": str(access_token),
                # "email": user.email,
                # "name": user.name
            }
        }, status=status.HTTP_201_CREATED)

    return Response(
        ErrorResponseSerializer({'error': serializer.errors}).data,
        status=status.HTTP_400_BAD_REQUEST
    )


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
                    'token': openapi.Schema(type=openapi.TYPE_STRING, description="JWT token"),
                    'user': openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'email': openapi.Schema(type=openapi.TYPE_STRING, format='email'),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                }
            )
        ),
        400: ErrorResponseSerializer,
        401: ErrorResponseSerializer
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            ErrorResponseSerializer({'error': serializer.errors}).data,
            status=status.HTTP_400_BAD_REQUEST
        )

    user = serializer.validated_data.get("user")
    if not user:
        return Response(
            ErrorResponseSerializer({'error': 'Invalid credentials'}).data,
            status=status.HTTP_401_UNAUTHORIZED
        )

    access_token = AccessToken.for_user(user)
    return Response({
        "message": "Login successful",
        "token": str(access_token),
        # "user": {
        #     "email": user.email,
        #     "name": user.name
        # }
    }, status=status.HTTP_200_OK)
