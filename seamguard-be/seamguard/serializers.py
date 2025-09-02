from rest_framework import serializers
from .models import User, EmployeeMaster,DashboardImage
from django.contrib.auth.hashers import make_password,check_password
from .models import Dashboard, Annotation, DetectionResult


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
        return data

    def create(self, validated_data):
        emp_id = validated_data['emp_id']
        try:
            employee = EmployeeMaster.objects.get(emp_id=emp_id)
        except EmployeeMaster.DoesNotExist:
            raise serializers.ValidationError("Employee not found.")

        if User.objects.filter(emp_id=emp_id).exists():
            raise serializers.ValidationError("User already registered with this emp_id.")

        user = User.objects.create(
            emp_id=emp_id,
            name=employee.name,
            line_number=employee.line_number,
            department=employee.department,
            phone_number=employee.phone_number,
            email=employee.email,
            password=make_password(validated_data['password'])
        )
        return user


class LoginSuccessSerializer(serializers.Serializer):
    message = serializers.CharField()
    user = serializers.DictField(child=serializers.CharField())
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['emp_id', 'name', 'email', 'phone_number', 'line_number', 'department', 'created_at', 'updated_at', 'is_active', 'is_staff']


class ErrorResponseSerializer(serializers.Serializer):
    error = serializers.CharField()


class RegisterSuccessSerializer(serializers.Serializer):
    message = serializers.CharField(default="Registration successful.")
    emp_id = serializers.CharField()
    email = serializers.EmailField()


class DashboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dashboard  # Assuming Dashboard model exists
        fields = ['emp_id', 'name', 'email', 'phone_number', 'line_number', 'department', 'created_at']


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)
    line_number = serializers.CharField()
    department = serializers.CharField()

    def validate(self, data):
        identifier = data['identifier']
        password = data['password']

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
            password=user.password  # or hash again if needed
        )




class DashboardImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardImage
        fields = ['id','emp_id', 'image', 'uploaded_at']



class AnnotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Annotation
        fields = '__all__'


class DetectionResultSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    class Meta:
        model = DetectionResult
        fields = '__all__'