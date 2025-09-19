from rest_framework import serializers
from .models import User, UserActivity
from django.contrib.auth import authenticate
import json
import os
import logging

logger = logging.getLogger(__name__)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'confirm_password']

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords must match"})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            username=validated_data['email']
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        logger.debug(f"Attempting login for email: {email}")

        # Check if the user is an admin from admins.json
        admins_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'admins.json')
        logger.debug(f"Checking admins.json at: {admins_file}")
        try:
            if os.path.exists(admins_file):
                with open(admins_file, 'r') as f:
                    admins_data = json.load(f)
                    logger.debug(f"Loaded admins.json: {admins_data}")
                    for admin in admins_data.get('admins', []):
                        if admin['email'] == email and admin['password'] == password:
                            logger.info(f"Admin credentials matched for {email}")
                            user, created = User.objects.get_or_create(
                                email=email,
                                defaults={
                                    'username': email,
                                    'name': 'Admin',
                                    'is_admin': True
                                }
                            )
                            if created:
                                logger.info(f"Created new admin user: {email}")
                                user.set_password(password)
                                user.save()
                            else:
                                logger.debug(f"Existing admin user found: {email}, is_admin: {user.is_admin}")
                            data["user"] = user
                            data["is_admin"] = True
                            return data
                        else:
                            logger.debug(f"No match for email: {email} in admins.json")
            else:
                logger.warning(f"admins.json not found at {admins_file}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in admins.json: {str(e)}")
            raise serializers.ValidationError("Server configuration error. Please contact support.")
        except Exception as e:
            logger.error(f"Error reading admins.json: {str(e)}")
            raise serializers.ValidationError("Server configuration error. Please contact support.")

        # Regular user authentication
        logger.debug(f"Falling back to Django authentication for {email}")
        user = authenticate(username=email, password=password)
        if not user:
            logger.error(f"Authentication failed for {email}")
            raise serializers.ValidationError("Invalid credentials")

        logger.info(f"User authenticated: {email}, is_admin: {getattr(user, 'is_admin', False)}")
        data["user"] = user
        data["is_admin"] = getattr(user, 'is_admin', False)
        return data

# serializer.py

class UserActivitySerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    name = serializers.CharField(source='user.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    is_admin = serializers.BooleanField(source='user.is_admin', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = UserActivity
        fields = ['activity_type', 'details', 'timestamp', 'user_id', 'username', 'is_admin', 'email', 'name']


class UserDetailSerializer(serializers.ModelSerializer):
    activities = UserActivitySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'name', 'is_admin', 'activities']

class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()