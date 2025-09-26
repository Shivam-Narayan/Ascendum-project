from rest_framework import serializers
from .models import User, EmployeeMaster, DashboardImage, Dashboard, Annotation, DetectionResult
from django.contrib.auth.hashers import make_password, check_password

# Define industry choices for serializers
INDUSTRY_CHOICES = [
    'Glass', 'Iron & Steel', 'FMCG', 'IT Hardware', 'Automobiles',
    'Apparels', 'Textiles', 'Furnitures', 'Leather', 'Fabricated Metals', 'CAD'
]

class EmployeeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeMaster
        fields = '__all__'

class RegisterUserFromEmpIDSerializer(serializers.Serializer):
    emp_id = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")

        emp_id = data['emp_id']
        try:
            employee = EmployeeMaster.objects.get(emp_id=emp_id)
            if not employee.industry or employee.industry not in INDUSTRY_CHOICES:
                raise serializers.ValidationError("Invalid or missing industry in employee record.")
            data['industry'] = employee.industry  # Add industry to validated data
        except EmployeeMaster.DoesNotExist:
            raise serializers.ValidationError("Employee not found.")

        if User.objects.filter(emp_id=emp_id).exists():
            raise serializers.ValidationError("User already registered with this emp_id.")

        return data

    def create(self, validated_data):
        emp_id = validated_data['emp_id']
        employee = EmployeeMaster.objects.get(emp_id=emp_id)  # Already validated in validate()

        user = User.objects.create(
            emp_id=emp_id,
            name=employee.name,
            line_number=employee.line_number,
            department=employee.department,
            phone_number=employee.phone_number,
            email=employee.email,
            industry=validated_data['industry'],  # Use industry from validated data
            password=make_password(validated_data['password'])
        )
        return user

class LoginSuccessSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = serializers.DictField(child=serializers.CharField())

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['emp_id', 'name', 'email', 'phone_number', 'line_number', 'department', 'industry', 'created_at', 'updated_at', 'is_active', 'is_staff']

class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()

class RegisterSuccessSerializer(serializers.Serializer):
    message = serializers.CharField(default="Registration successful.")
    emp_id = serializers.CharField()
    email = serializers.EmailField()
    industry = serializers.CharField()

class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard
        fields = ['emp_id', 'name', 'email', 'phone_number', 'line_number', 'department', 'industry', 'created_at']

class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)
    line_number = serializers.CharField()
    department = serializers.CharField()
    industry = serializers.ChoiceField(choices=INDUSTRY_CHOICES, required=True)

    def validate(self, data):
        identifier = data['identifier']
        password = data['password']
        industry = data['industry']

        try:
            user = User.objects.get(
                **(
                    {'email': identifier} if '@' in identifier else
                    {'phone_number': identifier} if identifier.isdigit() else
                    {'emp_id': identifier}
                )
            )
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        if not check_password(password, user.password):
            raise serializers.ValidationError("Invalid password.")

        if user.industry != industry:
            raise serializers.ValidationError("Industry does not match user's registered industry.")

        data['user'] = user
        return data

    def create(self, validated_data):
        user = validated_data['user']
        return Dashboard.objects.create(
            emp_id=user.emp_id,
            name=user.name,
            email=user.email,
            phone_number=user.phone_number,
            line_number=validated_data['line_number'],
            department=validated_data['department'],
            industry=validated_data['industry'],
            password=user.password
        )

class DashboardImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardImage
        fields = ['id', 'emp_id', 'image', 'uploaded_at', 'industry']

class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = ['id', 'user', 'image', 'class_name', 'x_min', 'y_min', 'x_max', 'y_max', 'industry']

class DetectionResultSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = DetectionResult
        fields = ['id', 'dashboard_user', 'emp_id', 'image_id', 'defect_result', 'created_at', 'batch_id', 'source', 'industry']